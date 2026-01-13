"""Agent-level recorder management.

This module provides the AgentRecorderManager class which manages the lifecycle
of recorders for agent-level observation recording. Each stream gets a single
recorder that is shared by all capabilities in that stream.
"""

import logging
import threading
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from highlighter.agent.capabilities.base_capability import _AppendableIterator
from highlighter.agent.capabilities.recorder import Recorder, RecordMode
from highlighter.core.enums import ContentTypeEnum


class AgentRecorderManager:
    """Manages agent-level recorders for observation recording.

    Handles the lifecycle of recorders that are shared across capabilities in a stream.
    Each stream gets a single recorder that all capabilities in that stream write to.

    This separates recorder management concerns from HLAgent, making the code more
    testable and maintainable.
    """

    def __init__(self, pipeline, logger: Optional[logging.Logger] = None):
        """Initialize the recorder manager.

        Args:
            pipeline: The pipeline instance to scan for capabilities
            logger: Optional logger instance (creates one if not provided)
        """
        self.pipeline = pipeline
        self.logger = logger or logging.getLogger(__name__)

        # Recorder state
        self._recorders: Dict[str, Recorder] = {}  # stream_id -> Recorder
        self._data_sample_iterators: Dict[str, _AppendableIterator] = {}  # stream_id -> Iterator
        self._recorder_init_lock = threading.Lock()  # Protect lazy initialization
        self._initialized_streams = set()  # Track which streams have initialized recorders
        self._stream_graph_paths: Dict[str, str] = {}  # stream_id -> graph_path

    def register_stream(self, stream_id: str, graph_path: str = None):
        """Register a stream's graph path for later use during recorder initialization.

        Args:
            stream_id: The stream ID to register
            graph_path: The graph path for this stream (defaults to main graph if None)
        """
        # If no graph_path provided, use the main graph (first element in pipeline graph)
        if graph_path is None:
            # Get the default graph path from pipeline graph
            graph_items = list(self.pipeline.pipeline_graph._graph.items())
            if graph_items:
                graph_path = graph_items[0][0]  # First graph node name
            else:
                graph_path = "default"  # Fallback

        self._stream_graph_paths[stream_id] = graph_path

    def ensure_initialized(self, stream_id: str):
        """Lazily initialize recorders for a stream on first use.

        This must be called from a context where the stream's thread-local storage
        is set up (e.g., during frame processing), not during create_stream().

        Thread-safe: uses a lock to prevent concurrent initialization of the same stream.

        Args:
            stream_id: The stream ID to initialize recorders for
        """
        # Fast path: check without lock if already initialized
        if stream_id in self._initialized_streams:
            return

        # Slow path: acquire lock and initialize if needed
        with self._recorder_init_lock:
            # Double-check after acquiring lock (another thread might have initialized)
            if stream_id in self._initialized_streams:
                return

            # Now safe to initialize since we're in a context with thread-local stream access
            self._initialize_for_stream(stream_id)
            self._initialized_streams.add(stream_id)

    def _initialize_for_stream(self, stream_id: str):
        """Initialize recorder for a stream.

        Creates a single recorder per stream that is shared by all capabilities in that stream.

        Args:
            stream_id: The stream ID to initialize recorder for
        """
        # Find any capability with recording enabled to get recording parameters
        recording_params = None
        recording_capabilities = []

        # Get the graph path from our stored mapping, fallback to default behavior
        head_node_name = self._stream_graph_paths.get(stream_id)
        if head_node_name is None:
            # Fallback: try to get from thread-local context if available
            try:
                head_node_name = self.pipeline.get_stream()[0].graph_path
            except AttributeError:
                # If thread-local access fails, use the first graph node as default
                graph_items = list(self.pipeline.pipeline_graph._graph.items())
                head_node_name = graph_items[0][0] if graph_items else "default"
                self.logger.warning(
                    f"Stream {stream_id} graph_path not registered, using default: {head_node_name}"
                )

        graph_path = self.pipeline.pipeline_graph.get_path(head_node_name)

        for node in graph_path:
            node_name = node.name
            capability = node.element

            # Check if this capability supports recording
            if not hasattr(capability, "recording_enabled"):
                continue

            # Check if recording is enabled for this capability and stream
            if not capability.recording_enabled(stream_id):
                continue

            recording_capabilities.append(node_name)

            # Get parameters from the first capability with recording enabled
            if recording_params is None:
                recording_params = capability.stream_parameters(stream_id)

        # If no capabilities have recording enabled, nothing to do
        if not recording_params:
            return

        database = getattr(recording_params, "database", None)
        record = getattr(recording_params, "record", None) or RecordMode.OFF

        # Only create recorder if record mode is not OFF
        if record is not RecordMode.OFF:
            # Validate required parameters before creating recorder
            if database is None:
                raise ValueError(f"Missing 'database' for stream '{stream_id}', required when recording")

            self.logger.info(
                f"Recording {len(recording_capabilities)} capabilities "
                f"({', '.join(recording_capabilities)}) to {record}",
                extra={"stream_id": stream_id, "capability_name": "AgentOutputRecorder"},
            )

            # Create appendable iterator for this stream
            data_sample_iterator = _AppendableIterator()
            self._data_sample_iterators[stream_id] = data_sample_iterator

            # Create recorder for this stream
            self._recorders[stream_id] = Recorder(
                iterator=data_sample_iterator,
                session_factory=lambda: Session(database.engine),
                content_type=ContentTypeEnum.ENTITIES,
                account_uuid=recording_params.data_source_uuid,
                data_source_uuid=recording_params.data_source_uuid,
                recording_state=recording_params.recording_state,
                record=recording_params.record,
                samples_per_file=recording_params.samples_per_file,
                seconds_per_file=recording_params.seconds_per_file,
                output_filename_template=recording_params.output_filename_template,
                output_folder=recording_params.output_folder,
                stream_id=stream_id,
                capability_name="AgentOutputRecorder",
            )

    def cleanup_stream(self, stream_id: str):
        """Cleanup recorders for a stream.

        Flushes and removes the recorder for this stream.

        Args:
            stream_id: The stream ID to cleanup
        """
        # Clean up this stream's recorder
        if stream_id in self._recorders:
            self._recorders[stream_id].flush()  # Blocks until recorder worker thread exits
            del self._recorders[stream_id]
        if stream_id in self._data_sample_iterators:
            del self._data_sample_iterators[stream_id]

        # Remove stream from initialized set and graph path mapping
        self._initialized_streams.discard(stream_id)
        self._stream_graph_paths.pop(stream_id, None)

    def record_data_sample(self, stream_id: str, data_sample):
        """Record a data sample to the stream's recorder.

        Args:
            stream_id: The stream ID to record to
            data_sample: The data sample to record
        """
        if stream_id not in self._recorders:
            return

        self._data_sample_iterators[stream_id].append(data_sample)
        next(self._recorders[stream_id])

    def get_recorder(self, stream_id: str) -> Optional[Recorder]:
        """Get the recorder for a stream, if it exists.

        Args:
            stream_id: The stream ID to get recorder for

        Returns:
            The Recorder instance, or None if no recorder exists for this stream
        """
        self.ensure_initialized(stream_id)
        return self._recorders.get(stream_id)

    def has_recorder(self, stream_id: str) -> bool:
        """Check if a recorder exists for a stream.

        Args:
            stream_id: The stream ID to check

        Returns:
            True if a recorder exists for this stream, False otherwise
        """
        return stream_id in self._recorders

    def get_recorders_for_capabilities(self, stream_id: str, capability_names: List[str]) -> List[Recorder]:
        """Get recorders for specified capabilities in a stream.

        This is used by CreateCase capability to collect recorders for coordinated recording.

        Handles two types of recorders:
        1. Agent-level recorders: For capability outputs (all capabilities share one per stream)
        2. DataSource recorders: For input video (stored in capability._dsps)

        Args:
            stream_id: The stream ID to get recorders for
            capability_names: List of capability names to get recorders for

        Returns:
            List containing the Recorder instance(s), or empty list if no recorder exists.
            - For agent-level recording: Returns the shared recorder for this stream
            - For DataSource recording: Returns the capability's _dsps recorder
        """
        recorders = []

        # Check if we have agent-level recorder (for capability outputs)
        self.ensure_initialized(stream_id)
        if stream_id in self._recorders:
            recorders.append(self._recorders[stream_id])

        # Also check for DataSource recorders (for input video)
        # DataSource capabilities have their own _dsps dict
        # get sub graph
        head_node_name = self._stream_graph_paths.get(stream_id)
        if head_node_name is None:
            # Fallback: try to get from thread-local context if available
            try:
                head_node_name = self.pipeline.get_stream()[0].graph_path
            except AttributeError:
                # If thread-local access fails, use the first graph node as default
                graph_items = list(self.pipeline.pipeline_graph._graph.items())
                head_node_name = graph_items[0][0] if graph_items else "default"

        graph_path = self.pipeline.pipeline_graph.get_path(head_node_name)
        for node in graph_path:
            node_name = node.name
            if node_name not in capability_names:
                continue

            capability = node.element
            # Check if this is a DataSource with its own _dsps
            if hasattr(capability, "_dsps") and stream_id in capability._dsps:
                recorders.append(capability._dsps[stream_id])

        if not recorders:
            self.logger.warning(
                f"No recorders found with capabilities {capability_names}. "
                f"Recording may not be enabled for this stream or these capabilities.",
                extra={"stream_id": stream_id},
            )

        return recorders

    def get_all_recorders_for_capabilities(self, capability_names: List[str]) -> List[Recorder]:
        """Get recorders for the supplied capability names across *all* streams."""

        all_recorders: List[Recorder] = []
        seen = set()
        stream_ids = set(self._stream_graph_paths.keys()) | set(self._recorders.keys())

        self.logger.debug(
            "get_all_recorders_for_capabilities: collecting from streams %s for capabilities %s",
            sorted(stream_ids) if stream_ids else "<none>",
            capability_names,
        )

        for stream_id in stream_ids:
            for recorder in self.get_recorders_for_capabilities(stream_id, capability_names):
                marker = id(recorder)
                if marker in seen:
                    continue
                seen.add(marker)
                # Diagnostic: log stream_id of each recorder
                self.logger.debug(
                    "Collected recorder with stream_id=%r, capability_name=%r from stream %s",
                    recorder._stream_id,
                    recorder._capability_name,
                    stream_id,
                )
                all_recorders.append(recorder)

        if not all_recorders:
            self.logger.warning(
                "No recorders found across streams %s for capabilities %s",
                sorted(stream_ids) if stream_ids else "<none>",
                capability_names,
            )

        return all_recorders
