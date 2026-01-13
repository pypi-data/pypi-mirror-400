import json
import queue
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

import litellm
from litellm import ModelResponse, completion
from litellm.caching.caching import Cache
from pydantic import Field, model_validator

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.agent.intelligence.context_builder import ContextBuilder
from highlighter.agent.intelligence.template_manager import TemplateManager
from highlighter.agent.triggers import OnCaseTrigger, TriggerUnion
from highlighter.client.base_models.entities import Entities
from highlighter.client.gql_client import HLClient, get_threadsafe_hlclient

__all__ = ["LLM"]


class LLM(Capability):
    """
    Parameters used by this capability:


    model: str: name of the model to use. Default: "claude-3-haiku-20240307"

    prompt_template: str: The prompt to use the context of the process_frame 'text'
        param will be inserted at {{PLACEHOLDER}}

    prompt_template_path: str: If used the `prompt_template` will be overwirtten
        with the contents of the template file.

    system_prompt_template: str: The system prompt template to use

    system_prompt_template_path: str: If used the `system_prompt_template` will be overwirtten
        with the contents of the template file.

    mock_response: bool: mock responses from llm, Defaut `true`

    num_retries: int: Number of retries. Default: 8

    completion_kwargs": {"temperature": 0.5}
        timeout: float | int | None = None
        temperature: float | None = None
        top_p: float | None = None
        n: int | None = None
        stream: bool | None = None
        stop: Unknown | None = None
        max_tokens: int | None = None
        presence_penalty: float | None = None
        frequency_penalty: float | None = None
        logit_bias: dict[Unknown, Unknown] | None = None
        user: str | None = None
        response_format: dict[Unknown, Unknown] | None = None
        seed: int | None = None
        tools: List[Unknown] | None = None
        tool_choice: str | None = None
        logprobs: bool | None = None
        top_logprobs: int | None = None
        deployment_id: Unknown | None = None
        extra_headers: dict[Unknown, Unknown] | None = None
        functions: List[Unknown] | None = None
        function_call: str | None = None
        base_url: str | None = None
        api_version: str | None = None
        api_key: str | None = None
        model_list: list[Unknown] | None = None
    """

    class InitParameters(Capability.InitParameters):
        cache_system_prompt: bool = False
        completion_kwargs: dict = {}
        mock_response: bool = True
        model: str = "claude-3-haiku-20240307"
        num_retries: int = 8
        prompt_template: Optional[str] = None
        system_prompt_template: Optional[str] = None

        # Frame and time windowing
        frame_window_size: Optional[int] = None
        time_window_seconds: Optional[float] = None

        # Tool calling configuration
        enable_tool_calling: bool = False
        available_tools: Optional[List[str]] = None  # None = all tools available
        debug_mode: bool = False  # Include full tool results in passthrough

        @model_validator(mode="after")
        def validate_window_sizes(self) -> "InitParameters":
            """Validate window size configuration"""
            # Ensure at least one window size is set, default to frame_window_size=1
            if self.frame_window_size is None and self.time_window_seconds is None:
                self.frame_window_size = 1

            # Validate window sizes if set
            if self.frame_window_size is not None and self.frame_window_size < 1:
                raise ValueError("frame_window_size must be at least 1")
            if self.time_window_seconds is not None and self.time_window_seconds <= 0:
                raise ValueError("time_window_seconds must be greater than 0")

            return self

    class StreamParameters(InitParameters):
        prompt_template_path: Optional[str] = None
        system_prompt_template_path: Optional[str] = None
        strategy: str
        prompt_output_dir: Optional[str] = None  # Directory to write prompts for debugging

        # FIXME: We have no 'nice' way of a Capability accepting input from
        # arbitrary up stream Capabilities without using something like **kwargs
        # this is an effort to try a new way of pooling outputs from upstream
        # Capabilities and only executing when have we all the required data.
        build_context_from: List[str]

        trigger: TriggerUnion = Field(default_factory=lambda: OnCaseTrigger())

    def _capability_label(self) -> str:
        """Get capability label from definition name or class name"""
        return getattr(getattr(self, "definition", None), "name", self.__class__.__name__)

    def __init__(self, context):
        super().__init__(context)
        self.prompt_template: str = self.init_parameters.prompt_template
        self.system_prompt_template: Optional[str] = self.init_parameters.system_prompt_template
        self._hl_credentials: Optional[Tuple[str, str]] = None

        # Initialize TemplateManager for Jinja2 template rendering
        self.template_manager = TemplateManager(use_jinja2=True, validate=True)

        self._context_builder = ContextBuilder(
            frame_window_size=self.init_parameters.frame_window_size,
            time_window_seconds=self.init_parameters.time_window_seconds,
            taxonomy=None,  # Will be configured via parameters
            content_filters=None,  # Will be configured via parameters
            stream_id=None,  # Multi-stream, so no single stream_id
        )
        self.logger.info("Initialize llm context builder")

        # Store pipeline graph reference for tool access to other capabilities
        self._pipeline_graph = None
        if hasattr(self.pipeline, "pipeline_graph"):
            self._pipeline_graph = self.pipeline.pipeline_graph

        # Background processing state
        self._background_queue = queue.Queue(maxsize=2)  # Limit to 2 pending jobs
        self._background_thread = None
        self._background_stop_event = threading.Event()
        self._background_lock = threading.Lock()

        litellm.cache = Cache(type="disk")
        litellm.success_callback = [self.log_success_event]
        litellm.failure_callback = [self.log_failure_event]
        litellm._logging._disable_debugging()

    def _get_threadsafe_hl_client(self) -> HLClient:
        """Return a thread-local HLClient for background tool calls."""
        if self._hl_credentials is None:
            base_client = HLClient.get_client()
            self._hl_credentials = (base_client.api_token, base_client.endpoint_url)

        api_token, endpoint_url = self._hl_credentials
        return get_threadsafe_hlclient(api_token, endpoint_url)

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        parameters = self.stream_parameters(stream.stream_id)
        log_extra = {"stream_id": stream.stream_id, "capability_name": self._capability_label()}

        self.logger.info(
            f"Starting stream with model: {parameters.model}, strategy: {parameters.strategy}",
            extra=log_extra,
        )

        # Load and compile prompt template using helper method
        prompt_template = self._load_template(self.prompt_template, parameters.prompt_template_path)
        if not prompt_template:
            self.logger.error("No prompt_template provided", extra=log_extra)
            return StreamEvent.ERROR, "Must supply 'prompt_template'"

        try:
            self.template_manager.compile(prompt_template, "prompt")
            self.logger.debug("Prompt template compiled successfully", extra=log_extra)
        except ValueError as e:
            self.logger.error(f"Prompt template compilation failed: {e}", extra=log_extra)
            return StreamEvent.ERROR, f"Prompt template compilation failed: {e}"

        # Load and compile system template (optional)
        system_template = self._load_template(
            self.system_prompt_template, parameters.system_prompt_template_path
        )
        if system_template:
            try:
                self.template_manager.compile(system_template, "system")
                self.logger.debug("System template compiled successfully", extra=log_extra)
            except ValueError as e:
                self.logger.error(f"System template compilation failed: {e}", extra=log_extra)
                return StreamEvent.ERROR, f"System template compilation failed: {e}"
        else:
            # Allow missing system prompt
            self.logger.warning("No system_prompt_template provided", extra=log_extra)

        # Validate templates with dummy context
        dummy_ctx = self._build_dummy_context()
        try:
            self.template_manager.validate_template("prompt", dummy_ctx)
            if "system" in self.template_manager.compiled_templates:
                self.template_manager.validate_template("system", dummy_ctx)
            self.logger.debug("Template validation successful", extra=log_extra)
        except ValueError as e:
            self.logger.error(f"Template validation failed: {e}", extra=log_extra)
            return StreamEvent.ERROR, f"Template validation failed: {e}"

        # Validate strategy parameter
        if parameters.strategy is None:
            self.logger.error("Agent parameter 'strategy' is not set", extra=log_extra)
            raise ValueError("Agent parameter 'strategy' is not set.")
        elif parameters.strategy in ["select_all", "pass", "completion"]:
            pass
        else:
            self.logger.error(f"Invalid strategy value: {parameters.strategy}", extra=log_extra)
            raise ValueError("Agent parameter 'strategy' needs valid value.")

        # Create output directory if specified
        if parameters.prompt_output_dir:
            import os

            os.makedirs(parameters.prompt_output_dir, exist_ok=True)
            self.logger.info(f"Prompts will be written to: {parameters.prompt_output_dir}", extra=log_extra)

        self.logger.info("Stream started successfully", extra=log_extra)

        # Start background processing thread if not already running
        self._ensure_background_thread_started()

        return StreamEvent.OKAY, None

    def stop_stream(self, stream, stream_id):
        """Clean up background thread when stream stops"""
        log_extra = {"stream_id": stream_id, "capability_name": self._capability_label()}
        self.logger.info("Stopping stream and background thread", extra=log_extra)

        # Signal background thread to stop
        self._background_stop_event.set()

        # Wait for thread to finish (with timeout)
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=10.0)
            if self._background_thread.is_alive():
                self.logger.warning("Background thread did not stop within timeout", extra=log_extra)

        return super().stop_stream(stream, stream_id)

    def _ensure_background_thread_started(self):
        """Start background processing thread if not already running"""
        with self._background_lock:
            if self._background_thread is None or not self._background_thread.is_alive():
                self._background_stop_event.clear()
                self._background_thread = threading.Thread(
                    target=self._background_worker, daemon=True, name="LLM-BackgroundWorker"
                )
                self._background_thread.start()
                self.logger.info("Background processing thread started")

    def _background_worker(self):
        """Background thread worker that processes LLM calls asynchronously"""
        self.logger.info("Background worker thread started")

        while not self._background_stop_event.is_set():
            try:
                # Wait for work with timeout to check stop event periodically
                work_item = self._background_queue.get(timeout=1.0)
            except queue.Empty:
                continue  # Check stop event and loop again

            if work_item is None:  # Poison pill to stop
                break

            try:
                # Unpack work item
                system_prompt, prompt, parameters, log_extra, stream = work_item

                self.logger.info("Background worker processing LLM request", extra=log_extra)

                # Call LLM (this blocks, but in background thread)
                event, llm_result = self._call_llm(system_prompt, prompt, parameters, log_extra, stream)

                if event == StreamEvent.ERROR:
                    self.logger.error(f"LLM call failed: {llm_result}", extra=log_extra)
                else:
                    self.logger.info("Background worker completed LLM request", extra=log_extra)

            except Exception as e:
                self.logger.error(f"Error in background worker: {e}", extra=log_extra, exc_info=True)
            finally:
                self._background_queue.task_done()

        self.logger.info("Background worker thread stopped")

    def process_frame(self, stream, data_samples, **kwargs) -> Tuple[StreamEvent, Union[Dict, str]]:
        """Process frame and add data to ContextBuilder

        Aggregates data_samples and entities from kwargs across all streams.
        """
        parameters = self.stream_parameters(stream.stream_id)

        # Get current frame_id from stream
        frame_id = None
        if stream.frames and len(stream.frames) > 0:
            frame_ids = list(stream.frames.keys())
            if frame_ids:
                frame_id = frame_ids[-1]

        log_extra = {
            "stream_id": stream.stream_id,
            "capability_name": self._capability_label(),
            "frame_id": frame_id,
        }

        # Step 1: Collect entities from stream
        entities_dict = self._collect_entities_from_stream(stream, parameters, log_extra)
        self.logger.info(
            f"entities_dict in process_frame: len={len(entities_dict)}, "
            f"keys={list(entities_dict.keys()) if entities_dict else 'None'}",
            extra=log_extra,
        )
        # Log each entity's details
        for entity_id, entity in entities_dict.items():
            self.logger.info(
                f"  Entity {entity_id}: annotations={len(entity.annotations)}, "
                f"global_obs={len(entity.global_observations)}",
                extra=log_extra,
            )
            # Show last few annotations with their observations
            for i, annotation in enumerate(list(entity.annotations)[-3:]):
                obs_count = len(annotation.observations)
                self.logger.info(
                    f"    Annotation {i}: {obs_count} observations",
                    extra=log_extra,
                )
                # Show last 3 observations from this annotation
                for j, obs in enumerate(list(annotation.observations)[-3:]):
                    attr_name = getattr(obs.attribute_id, "label", str(obs.attribute_id))
                    self.logger.info(
                        f"      Obs {j}: attribute={attr_name}, value={obs.value}, occurred_at={obs.occurred_at}",
                        extra=log_extra,
                    )

        # Step 2: Get current sample time for time window calculations
        current_sample_time = data_samples[0].recorded_at if data_samples else None

        # Step 3: Check if time window is full (only after recording has started)
        # This allows time-based windows to work independently of triggers
        # but only after we've started accumulating data
        time_window_full = False
        if (
            self._context_builder.time_window_seconds is not None
            and self._context_builder._window_start_time is not None  # Only check if we've started recording
            and self._context_builder.is_window_full(current_sample_time)
        ):
            time_window_full = True
            elapsed = (current_sample_time - self._context_builder._window_start_time).total_seconds()
            self.logger.info(
                f"Time window full: {elapsed:.2f}s >= {self._context_builder.time_window_seconds}s",
                extra=log_extra,
            )

        # Step 4: Accumulate data if trigger fires OR if time window is full
        trigger_state = parameters.trigger.get_state(stream)

        trigger_state = False
        # Check if we have access to a case for tool calling
        task_context_check = self._get_task_context_for_tools(stream)
        case_id_available = None
        task_context_source = "none"

        if task_context_check:
            task_context_source = "found"
            if hasattr(task_context_check, "_recording") and task_context_check._recording:
                recording_session = task_context_check._recording[-1]
                if hasattr(recording_session, "case_id"):
                    case_id_available = recording_session.case_id
                    trigger_state = True
                    task_context_source = f"found_with_case_{case_id_available}"
                else:
                    task_context_source = "found_no_case_id"
            else:
                task_context_source = "found_no_recording"

        self.logger.info(
            f"Trigger state: {trigger_state}, case_id: {case_id_available}, task_context: {task_context_source}",
            extra=log_extra,
        )

        if trigger_state or time_window_full:
            self.logger.info(
                f"Accumulating data - trigger: {trigger_state}, time_window_full: {time_window_full}, "
                f"context_builder_id={id(self._context_builder)}, "
                f"entities_dict has {len(entities_dict)} entities",
                extra=log_extra,
            )
            self._accumulate_data_if_triggered(
                stream, data_samples, entities_dict, parameters, log_extra, trigger_state
            )

        # Log current state of context builder observations
        self._log_context_builder_observations(log_extra)

        # Step 5: Check if window is full, return early if not
        if not self._context_builder.is_window_full(current_sample_time):
            accumulated = self._context_builder.get_accumulated_count()

            # Calculate time window progress
            time_progress_str = "N/A"
            if (
                self._context_builder.time_window_seconds is not None
                and self._context_builder._window_start_time is not None
            ):
                # Use the latest timestamp from accumulated samples for progress calculation
                if self._context_builder._data_samples:
                    latest_time = max(sample.recorded_at for sample in self._context_builder._data_samples)
                    elapsed = (latest_time - self._context_builder._window_start_time).total_seconds()
                elif current_sample_time is not None:
                    elapsed = (current_sample_time - self._context_builder._window_start_time).total_seconds()
                else:
                    elapsed = 0

                time_window_size = self._context_builder.time_window_seconds
                time_progress_pct = (elapsed / time_window_size) * 100 if time_window_size > 0 else 0
                time_progress_str = f"{elapsed:.1f}/{time_window_size}s ({time_progress_pct:.0f}%)"

            self.logger.info(
                f"Window not full yet: {accumulated}/{self._context_builder.frame_window_size or 'N/A'} frames, "
                f"time: {time_progress_str}",
                extra=log_extra,
            )
            return StreamEvent.OKAY, {"data_samples": data_samples, **kwargs}

        # Determine which condition triggered the window to be full
        frame_full = (
            self._context_builder.frame_window_size is not None
            and self._context_builder.get_accumulated_count() >= self._context_builder.frame_window_size
        )

        trigger_reason = []
        if frame_full:
            trigger_reason.append(
                f"frames: {self._context_builder.get_accumulated_count()}/{self._context_builder.frame_window_size}"
            )
        if time_window_full:
            elapsed = (current_sample_time - self._context_builder._window_start_time).total_seconds()
            trigger_reason.append(f"time: {elapsed:.1f}/{self._context_builder.time_window_seconds}s")

        self.logger.info(
            f"Window full - submitting to background thread {self._context_builder.get_accumulated_count()} samples "
            f"({', '.join(trigger_reason)})",
            extra=log_extra,
        )

        # Step 4: Build context and render prompts
        context = self._context_builder.build_context()
        system_prompt, prompt = self._render_prompts(context, parameters, stream.stream_id, log_extra)

        # Step 5: Submit work to background thread (non-blocking)
        try:
            # Try to add to queue without blocking
            self._background_queue.put_nowait((system_prompt, prompt, parameters, log_extra, stream))
            self._context_builder.clear()
            self.logger.info(
                f"Submitted LLM request to background thread (queue size: {self._background_queue.qsize()})",
                extra=log_extra,
            )
        except queue.Full:
            # Queue is full, log warning but continue processing frames
            self.logger.warning(
                f"Background queue full ({self._background_queue.qsize()} items), "
                "skipping this LLM call to avoid blocking frame processing",
                extra=log_extra,
            )

        # Step 6: Return immediately without waiting for LLM response
        # This allows the pipeline to continue processing frames
        self.logger.info("Continuing frame processing without waiting for LLM", extra=log_extra)
        return StreamEvent.OKAY, {"data_samples": data_samples, **kwargs}

    def _collect_entities_from_stream(self, stream, parameters, log_extra: dict) -> Entities:
        """Collect entities from stream frames based on build_context_from parameter

        Args:
            stream: Stream object containing frames
            parameters: Stream parameters with build_context_from configuration
            log_extra: Extra logging context (stream_id, capability)

        Returns:
            Entities object with collected entities
        """
        entities_dict = Entities()

        # Collect from stream.frames[frame_id].swag (entities stored in frame swag)
        if stream.frames and len(stream.frames) > 0:
            frame_ids = list(stream.frames.keys())
            if frame_ids:
                most_recent_frame = stream.frames[frame_ids[-1]]
                self.logger.info(
                    f"Collecting entities from frame {frame_ids[-1]}, keys: {parameters.build_context_from}",
                    extra=log_extra,
                )
                for entity_key in parameters.build_context_from:
                    entities_from_swag = most_recent_frame.swag.get(entity_key, {})
                    if entities_from_swag:
                        entities_dict.merge(entities_from_swag, strategy="append")
                        self.logger.info(
                            f"Merged entities from key '{entity_key}': {len(entities_from_swag)} entities",
                            extra=log_extra,
                        )
        else:
            self.logger.info("No frames available to collect entities from", extra=log_extra)

        return entities_dict

    def _accumulate_data_if_triggered(
        self, stream, data_samples, entities_dict, parameters, log_extra: dict, trigger_state: bool
    ):
        """Add data to context builder if trigger condition is met

        Args:
            stream: Stream object
            data_samples: List of DataSample objects
            entities_dict: Entities to add
            parameters: Stream parameters with trigger configuration
            log_extra: Extra logging context (stream_id, capability)
            trigger_state: Pre-computed trigger state from process_frame() (ensures consistency in multi-stream mode)
        """
        # Use the trigger_state passed from process_frame() instead of re-evaluating
        # This ensures we use the case_id-based trigger logic consistently

        # Check case availability when accumulating
        task_context = self._get_task_context_for_tools(stream)
        case_id = None
        if task_context and hasattr(task_context, "_recording") and task_context._recording:
            recording_session = task_context._recording[-1]
            if hasattr(recording_session, "case_id"):
                case_id = recording_session.case_id

        if trigger_state:
            # Log what we're adding BEFORE merge
            self.logger.info(
                f"BEFORE add_to_context: entities_dict has {len(entities_dict)} entities",
                extra=log_extra,
            )
            for entity_id, entity in entities_dict.items():
                self.logger.info(
                    f"  Adding entity {str(entity_id)[:8]}: {len(entity.annotations)} annotations",
                    extra=log_extra,
                )

            self._context_builder.add_to_context(
                data_samples=data_samples,
                entities=entities_dict if entities_dict else None,
                template_vars=None,  # Can be extended later
            )
            self.logger.info(
                f"Added {len(data_samples)} samples to context (case: {case_id})",
                extra=log_extra,
            )

    def _log_context_builder_observations(self, log_extra: dict):
        """Log the current state of observations in the context builder

        Args:
            log_extra: Extra logging context (stream_id, capability)
        """
        # Log context builder info
        self.logger.info(
            f"Context builder id={id(self._context_builder)}, "
            f"entities_buffer has {len(self._context_builder._entities_buffer)} entities, "
            f"data_samples={len(self._context_builder._data_samples)}",
            extra=log_extra,
        )

        # Check if context builder has any accumulated entities
        if self._context_builder._entities_buffer and len(self._context_builder._entities_buffer) > 0:
            # Log details about entities in buffer
            for entity_id, entity in list(self._context_builder._entities_buffer.items())[:3]:  # Show first 3
                self.logger.info(
                    f"  Buffered entity {str(entity_id)[:8]}: {len(entity.annotations)} annotations",
                    extra=log_extra,
                )
                # Log annotation IDs to detect duplicates
                annotation_ids = [str(a.id)[:8] for a in list(entity.annotations)[:10]]
                self.logger.info(
                    f"    Annotation IDs: {annotation_ids}",
                    extra=log_extra,
                )

            context = self._context_builder.build_context()
            obs_count = len(context.observations)

            self.logger.info(
                f"Context builder state: {obs_count} observation(s) accumulated",
                extra=log_extra,
            )

            # show() will log the table using its own logger
            context.observations.show(log_extra=log_extra)
        else:
            self.logger.info(
                "Context builder observations: No entities accumulated yet",
                extra=log_extra,
            )

    def _render_prompts(self, context, parameters, stream_id, log_extra: dict) -> Tuple[str, str]:
        """Render system and user prompts using Jinja2 templates

        Args:
            context: TemplateContext object
            parameters: Stream parameters
            stream_id: Stream identifier
            log_extra: Extra logging context (stream_id, capability)

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        self.logger.debug("Rendering prompts with Jinja2 templates", extra=log_extra)

        system_prompt = self.template_manager.render("system", context)
        prompt = self.template_manager.render("prompt", context)

        self.logger.debug(
            f"Rendered prompts - system: {len(system_prompt)} chars, user: {len(prompt)} chars",
            extra=log_extra,
        )

        # Write prompts to output directory if configured
        if parameters.prompt_output_dir:
            self._write_prompts_to_file(
                parameters.prompt_output_dir, stream_id, system_prompt, prompt, log_extra
            )

        return system_prompt, prompt

    def _call_llm(
        self, system_prompt: str, prompt: str, parameters, log_extra: dict, stream=None
    ) -> Tuple[StreamEvent, Union[str, Dict]]:
        """Call LLM with rendered prompts and optional tool calling support

        Args:
            system_prompt: Rendered system prompt
            prompt: Rendered user prompt
            parameters: Stream parameters with model configuration
            log_extra: Extra logging context (stream_id, capability)
            stream: Stream object (required for tool execution)

        Returns:
            Tuple of (StreamEvent, result_dict_with_content_and_tool_results)
        """
        try:
            messages = self._build_messages(system_prompt, prompt, parameters)

            # Prepare completion kwargs with optional tools
            completion_kwargs = parameters.completion_kwargs.copy()

            # Add tools if enabled
            tools = []
            if parameters.enable_tool_calling:
                tools = self._get_available_tools(log_extra["stream_id"])
                if tools:
                    completion_kwargs["tools"] = tools
                    self.logger.debug(
                        f"Tool calling enabled with {len(tools)} tools available",
                        extra=log_extra,
                    )

            if parameters.mock_response:
                self.logger.info("Using mock LLM response", extra=log_extra)
                mock_content = json.dumps([{"mock_response": "mock_response_value"}] * 3)
                content = mock_content
                tool_calls = None
            else:
                self.logger.info(
                    f"Calling LLM model: {parameters.model}, retries: {parameters.num_retries}"
                    + (f", tools: {len(tools)}" if tools else ""),
                    extra=log_extra,
                )
                response: ModelResponse = completion(
                    model=parameters.model,
                    messages=messages,
                    num_retries=parameters.num_retries,
                    caching=True,
                    **completion_kwargs,
                )

                # Extract tool calls if present
                message = response["choices"][0]["message"]
                content = message.get("content", "")
                tool_calls = message.get("tool_calls", None)

            # Log response
            if content:
                self.logger.info(
                    f"LLM response received: {len(content)} chars\n{content}",
                    extra=log_extra,
                )

            # Execute tool calls if present
            tool_results = []
            if tool_calls and stream:
                self.logger.debug(
                    f"LLM requested {len(tool_calls)} tool call(s)",
                    extra=log_extra,
                )
                for tool_call in tool_calls:
                    result = self._execute_tool(stream, tool_call)
                    tool_results.append(result)

            # self._context_builder.clear()

            # Return content and tool results
            return StreamEvent.OKAY, {
                "content": content,
                "tool_calls": tool_calls,
                "tool_results": tool_results,
            }

        except Exception as e:
            message = f"Error while calling Litellm.completion, got: {e}"
            self.logger.error(message, extra=log_extra)
            return StreamEvent.ERROR, {"diagnostic": message}

    def _build_messages(self, system_prompt: str, prompt: str, parameters) -> List[Dict]:
        """Build messages array for LLM call

        Args:
            system_prompt: System prompt text
            prompt: User prompt text
            parameters: Stream parameters with cache configuration

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add system message with rendered system prompt
        if system_prompt:
            system = []
            if parameters.cache_system_prompt:
                system.append(
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                )
            else:
                system.append({"type": "text", "text": system_prompt})

            messages.append({"content": system, "role": "system"})

        # Add user message with rendered prompt
        messages.append({"content": prompt, "role": "user"})

        return messages

    def _build_response(
        self, llm_result: Dict, prompt: str, system_prompt: str, data_samples, kwargs, parameters
    ) -> Tuple[StreamEvent, Dict]:
        """Build response dictionary with LLM output, tool results, and pass-through data

        Args:
            llm_result: Dict with 'content', 'tool_calls', 'tool_results' from LLM
            prompt: User prompt that was sent
            system_prompt: System prompt that was sent
            data_samples: Original data samples
            kwargs: Additional kwargs to pass through
            parameters: Stream parameters (for debug_mode check)

        Returns:
            Tuple of (StreamEvent.OKAY, response_data)
        """
        content = llm_result.get("content", "")
        tool_results = llm_result.get("tool_results", [])

        response_data = {
            "text": content,
            "llm_prompt": prompt,
            "llm_system_prompt": system_prompt,
            "data_samples": data_samples,
        }

        # Add tool call info if tools were used
        # Store as JSON string to avoid collision with entity detection (which treats dicts as entities)
        if tool_results:
            tool_info = {
                "summary": {
                    "count": len(tool_results),
                    "tools_used": [r["tool"] for r in tool_results],
                    "success_count": sum(1 for r in tool_results if r["success"]),
                    "messages_created": sum(
                        1 for r in tool_results if r["tool"] == "create_message_on_case" and r["success"]
                    ),
                },
                # Include full tool results if debug mode enabled
                "detail": tool_results if parameters.debug_mode else None,
            }
            # Store as JSON string so agent.py doesn't treat it as entities
            response_data["llm_tools_json"] = json.dumps(tool_info)

        response_data.update(kwargs)
        return StreamEvent.OKAY, response_data

    def _get_available_tools(self, stream_id: str) -> List[Dict]:
        """Get tool schemas based on configuration.

        Args:
            stream_id: Stream identifier

        Returns:
            List of tool schemas in OpenAI/Anthropic format
        """
        from highlighter.agent.intelligence.tools import LLMTools

        parameters = self.stream_parameters(stream_id)

        if not parameters.enable_tool_calling:
            return []

        all_tools = LLMTools.get_tool_schemas()

        # Filter if specific tools configured
        if parameters.available_tools is not None:
            available_names = set(parameters.available_tools)
            return [t for t in all_tools if t["function"]["name"] in available_names]

        return all_tools

    def _get_task_context_for_tools(self, stream) -> Optional:
        """Get current recording TaskContext for tool execution.

        Follows the pattern from CreateCase capability to access TaskContext
        via stream variables or shared context.

        Args:
            stream: Stream object

        Returns:
            TaskContext if case is recording, None otherwise
        """
        log_extra = {"stream_id": stream.stream_id, "capability_name": self._capability_label()}

        # First check stream variables (per-stream context)
        if hasattr(stream, "variables"):
            task_context = stream.variables.get("create_case_task_context")
            if task_context:
                self.logger.debug("Found task_context in stream.variables", extra=log_extra)
                return task_context

        # Check record_all_streams shared state (for multi-stream recording)
        # Access the global shared state dictionary directly, same as CreateCase does
        try:
            from highlighter.agent.capabilities.create_case import (
                _RECORD_ALL_STREAMS_STATES,
            )

            # Get the key using the same logic as CreateCase._get_record_all_streams_state()
            key_source = getattr(self.pipeline, "agent", None) or self.pipeline
            key = id(key_source)

            shared_state = _RECORD_ALL_STREAMS_STATES.get(key)
            if shared_state:
                self.logger.info(
                    f"Shared state: active={shared_state.active}, "
                    f"has_task_context={shared_state.task_context is not None}, "
                    f"owner={shared_state.owner_stream_id}",
                    extra=log_extra,
                )
                if shared_state.active and shared_state.task_context:
                    self.logger.info(
                        f"Found task_context in record_all_streams shared state (owner: {shared_state.owner_stream_id})",
                        extra=log_extra,
                    )
                    return shared_state.task_context
            else:
                self.logger.debug(f"No shared state found for key {key}", extra=log_extra)
        except Exception as e:
            self.logger.debug(f"Error accessing shared state: {e}", extra=log_extra)

        # Fall back to pipeline graph lookup if available
        if self._pipeline_graph:
            # Try to find CreateCase capability's _shared_task_context
            for node in self._pipeline_graph.nodes:
                if hasattr(node, "element") and hasattr(node.element, "_shared_task_context"):
                    task_context = node.element._shared_task_context
                    if task_context:
                        self.logger.debug(
                            "Found task_context in CreateCase._shared_task_context", extra=log_extra
                        )
                        return task_context

        self.logger.debug("No task_context found", extra=log_extra)
        return None

    def _build_tool_context(self, stream):
        """Build ToolExecutionContext for tool calls.

        Args:
            stream: Stream object

        Returns:
            ToolExecutionContext with current stream/case information
        """
        from highlighter.agent.intelligence.tools import ToolExecutionContext

        log_extra = {"stream_id": stream.stream_id, "capability_name": self._capability_label()}

        # Get TaskContext for case access
        task_context = self._get_task_context_for_tools(stream)

        # Get case_id if recording
        case_id = None
        if task_context and hasattr(task_context, "_recording"):
            recording_deque = task_context._recording
            if recording_deque:
                # Get the most recent recording session
                recording_session = recording_deque[-1]
                if hasattr(recording_session, "case_id"):
                    case_id = recording_session.case_id
                    self.logger.debug(f"Building tool context with case: {case_id}", extra=log_extra)
                else:
                    self.logger.warning("Recording session missing case_id", extra=log_extra)
            else:
                self.logger.debug("No recording in progress", extra=log_extra)
        else:
            self.logger.debug("No task_context available for tools", extra=log_extra)

        # Get stream variables
        data_source_uuid = None
        account_uuid = None
        if hasattr(stream, "variables"):
            data_source_uuid = stream.variables.get("data_source_uuid")
            account_uuid = stream.variables.get("account_uuid")

        return ToolExecutionContext(
            stream=stream,
            logger=self.logger,
            client=self._get_threadsafe_hl_client(),
            task_context=task_context,
            case_id=case_id,
            stream_id=stream.stream_id,
            capability_name=self._capability_label(),
            data_source_uuid=data_source_uuid,
            account_uuid=account_uuid,
        )

    def _execute_tool(self, stream, tool_call) -> Dict[str, Any]:
        """Execute a single tool call with error handling.

        Args:
            stream: Stream object
            tool_call: Tool call from LLM response

        Returns:
            Dict with tool execution result
        """
        import json

        from highlighter.agent.intelligence.tools import LLMTools

        function = tool_call.function
        tool_name = function.name
        log_extra = {"stream_id": stream.stream_id, "capability_name": self._capability_label()}

        try:
            # Parse arguments
            args = json.loads(function.arguments) if function.arguments else {}

            self.logger.debug(
                f"Executing tool: {tool_name} with args: {args}",
                extra=log_extra,
            )

            # Build execution context
            ctx = self._build_tool_context(stream)

            # Get tool function
            tool_fn = LLMTools.get_tool_function(tool_name)
            if not tool_fn:
                raise ValueError(f"Unknown tool: {tool_name}")

            # Execute tool
            result = tool_fn(ctx, **args)

            # Log success at INFO level for key milestone (e.g., message sent to case)
            if result.get("success", True):
                self.logger.info(
                    f"Tool executed successfully: {tool_name}",
                    extra=log_extra,
                )
            else:
                self.logger.debug(
                    f"Tool execution completed with failure: {tool_name}",
                    extra=log_extra,
                )

            return {
                "tool": tool_name,
                "args": args,
                "result": result,
                "success": result.get("success", True),
            }

        except Exception as e:
            self.logger.warning(
                f"Tool execution failed: {tool_name} - {e}",
                extra=log_extra,
            )

            # Return error in structured format (still allows pipeline to continue)
            return {
                "tool": tool_name,
                "args": {},
                "result": {"error": str(e)},
                "success": False,
            }

    def _load_template(self, template: Optional[str], path: Optional[str]) -> Optional[str]:
        """Load template from string or file

        Args:
            template: Template string
            path: Path to template file

        Returns:
            Template string from path if provided, otherwise returns template parameter
        """
        if path:
            with open(path, "r") as f:
                return f.read()
        return template

    def _build_dummy_context(self):
        """Build dummy context for template validation

        Creates a minimal TemplateContext with dummy data to validate
        that templates can be rendered without errors.

        Returns:
            TemplateContext with dummy data
        """
        from datetime import datetime

        class DummyDataSample:
            stream_frame_index = 0
            content_type = "image"
            recorded_at = datetime.now()
            wh = (1920, 1080)

        # Create temporary context builder for validation
        from highlighter.agent.intelligence.context_builder import ContextBuilder

        temp_builder = ContextBuilder(frame_window_size=1, stream_id="validation")
        temp_builder.add_to_context([DummyDataSample()], None, {})
        return temp_builder.build_context()

    def _write_prompts_to_file(
        self, output_dir: str, stream_id: str, system_prompt: str, user_prompt: str, log_extra: dict
    ) -> None:
        """Write rendered prompts to files for debugging

        Args:
            output_dir: Directory to write prompt files
            stream_id: Stream identifier for filename
            system_prompt: Rendered system prompt
            user_prompt: Rendered user prompt
            log_extra: Extra logging context (stream_id, capability)
        """
        import os
        from datetime import datetime

        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        base_filename = f"{stream_id}_{timestamp}"

        # Write system prompt
        if system_prompt:
            system_path = os.path.join(output_dir, f"{base_filename}_system.txt")
            try:
                with open(system_path, "w") as f:
                    f.write(system_prompt)
                self.logger.debug(f"Wrote system prompt to: {system_path}", extra=log_extra)
            except Exception as e:
                self.logger.warning(f"Failed to write system prompt: {e}", extra=log_extra)

        # Write user prompt
        user_path = os.path.join(output_dir, f"{base_filename}_user.txt")
        try:
            with open(user_path, "w") as f:
                f.write(user_prompt)
            self.logger.debug(f"Wrote user prompt to: {user_path}", extra=log_extra)
        except Exception as e:
            self.logger.warning(f"Failed to write user prompt: {e}", extra=log_extra)

    def write_log(self, response_type, kwargs, response_obj, start_time, end_time):
        time_log_msgs = []
        if start_time is not None and end_time is not None:
            time_log_msgs.append(f"time: {timedelta_to_readable(end_time - start_time)}")

        base_log_messages = []

        if "response_cost" in kwargs:
            base_log_messages.append(f'response_cost: {round(kwargs["response_cost"], 6)}')

        if "cache_hit" in kwargs:
            cache_hit_y_n = "y" if kwargs["cache_hit"] else "n"
            base_log_messages.append(f"response_cache: {cache_hit_y_n}")

        identity_log_messages = []
        response_log_messages = []

        content = []

        if response_obj is not None:
            try:
                content = json.loads(response_obj["choices"][0]["message"]["content"])
                content = content if isinstance(content, list) else [content]
            except:
                raise ValueError(f"Couldn't parse response content: '{response_obj}'")

            if "usage" in response_obj:
                usage = response_obj["usage"]

                if "cache_creation_input_tokens" in usage:
                    prompt_cache_input_tokens = usage["cache_creation_input_tokens"]
                    if prompt_cache_input_tokens > 0:
                        response_log_messages.append(
                            f"prompt_cache_input_tokens: {prompt_cache_input_tokens}"
                        )

                if "cache_read_input_tokens" in usage:
                    cache_read_input_tokens = usage["cache_read_input_tokens"]
                    if cache_read_input_tokens > 0:
                        response_log_messages.append(
                            f"prompt_cache_read_input_tokens: {cache_read_input_tokens}"
                        )

        identity_log_messages = [json.dumps(content[0])]

        self.logger.info(
            f"LLM {response_type} "
            + " ".join(
                map(str, identity_log_messages + time_log_msgs + base_log_messages + response_log_messages)
            )
        )

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.write_log("success", kwargs, response_obj, start_time, end_time)

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self.write_log("failure", kwargs, response_obj, start_time, end_time)


def timedelta_to_readable(time_delta):
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = time_delta.microseconds // 1000  # Convert microseconds to milliseconds

    time_parts = []
    if days > 0:
        time_parts.append(str(days))
    if hours > 0 or days > 0:
        time_parts.append(f"{str(hours)}hr")
    if minutes > 0 or hours > 0 or days > 0:
        time_parts.append(f"{str(minutes)}min")
    if seconds > 0 or minutes > 0 or hours > 0 or days > 0:
        time_parts.append(f"{str(seconds)}s")
    if milliseconds > 0 or len(time_parts) > 0:
        time_parts.append(f"{str(milliseconds)}ms")

    return " ".join(time_parts)
