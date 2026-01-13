from __future__ import annotations

import logging
import time
from abc import abstractmethod
from collections import defaultdict
from typing import Annotated, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from highlighter.agent.observations_table import ObservationsTable
from highlighter.client.base_models.entities import Entities, Entity

logger = logging.getLogger(__name__)

__all__ = ["Trigger", "PeriodicTrigger", "OnCaseTrigger", "RuleTrigger", "TriggerUnion"]


class Trigger(BaseModel):

    capability_name: Optional[str] = None
    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    def get_state(self, stream, **kwargs) -> bool:
        """Returns True if trigger is in 'on' state, False if in 'off' state."""
        raise NotImplementedError()


class PeriodicTrigger(Trigger):
    type: Literal["PeriodicTrigger"] = "PeriodicTrigger"
    on_period: float = 30.0  # sec
    off_period: float = 300.0  # sec

    _start_time: Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _is_on_period(self) -> bool:
        """Determines if the current time is within an 'on' period."""
        current_time = time.time()

        if self._start_time is None:
            self._start_time = current_time

        elapsed = current_time - self._start_time
        cycle_time = self.on_period + self.off_period

        if cycle_time <= 0:
            # Avoid division by zero; default to 'on' if periods are non-positive.
            return True

        cycle_position = elapsed % cycle_time
        return cycle_position < self.on_period

    def get_state(self, *args, **kwargs) -> bool:
        """Returns True if in 'on' period, False if in 'off' period."""
        return self._is_on_period()


class OnCaseTrigger(Trigger):
    """Return true when a case is active, false when it's not"""

    type: Literal["OnCaseTrigger"] = "OnCaseTrigger"

    def get_state(self, stream, **kwargs) -> bool:
        return "create_case_task_context" in stream.variables


class RuleTrigger(Trigger):
    """Evaluate a CEL expression against the available trigger context."""

    type: Literal["RuleTrigger"] = "RuleTrigger"

    expression: str
    expected_entities: List[str]
    patience: int = 0  # sec - time to wait after last True before returning False
    default_state: bool = False
    log_errors_every_n_frames: int = 100  # Log evaluation errors once every N frames (0 = always log)

    _attribute_collection_warnings: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _evaluation_error_count: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _program_cache: dict = PrivateAttr(default_factory=dict)

    _entity_buffer: ClassVar[Dict] = dict()

    def __init__(self, **data):
        super().__init__(**data)
        self._last_true_trigger = None
        self._prev_state = self.default_state

    def get_state(self, stream, *, data_sample, **kwargs) -> bool:

        # Log entry with stream info
        log_extra = {"stream_id": stream.stream_id, "capability_name": self.capability_name or "RuleTrigger"}
        logger.debug(
            "=== get_state() called ===",
            extra=log_extra,
        )

        is_entities = lambda x: isinstance(x, Entities) or (
            isinstance(x, dict) and x and isinstance(x[list(x)[0]], Entity)
        )

        self._entity_buffer.update(kwargs)
        logger.debug(f"{self._entity_buffer.keys()}", extra=log_extra)
        if not all([e in self._entity_buffer for e in self.expected_entities]):
            logger.debug(
                f"s:{stream.stream_id} - no trigger update, {self._entity_buffer.keys()}", extra=log_extra
            )
            return self._prev_state
        logger.debug(f"s:{stream.stream_id} - evaluating trigger", extra=log_extra)

        # if "beaking" in kwargs:
        #    print(ColourStr.green(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))
        # elif ("clustering" in kwargs) and ("motion" in kwargs):
        #    print(ColourStr.blue(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))
        # else:
        #    print(ColourStr.red(f"s:{stream.stream_id} - RuleTrigger: {kwargs}"))

        observations_table = ObservationsTable()
        for ents in self._entity_buffer.values():
            for e in ents.values():
                observations_table.add_entity(e, data_sample, stream.stream_id)

        # If no rows exist in the observations table (entities with no observations or no entities),
        # create a row with data_sample info but no entity data
        # This allows data_sample expressions to be evaluated even when no entities/observations are detected
        if len(observations_table._rows) == 0:
            data_sample_row = ObservationsTable.Row(
                entity=None,  # No entity detected
                stream=ObservationsTable.Row.Stream(id=stream.stream_id),
                data_sample=ObservationsTable.Row.DataSample(
                    recorded_at=data_sample.recorded_at,
                    content_type=data_sample.content_type,
                    stream_frame_index=data_sample.stream_frame_index,
                    media_frame_index=data_sample.media_frame_index,
                ),
                annotation=None,  # No annotation
                attribute={},
            )
            observations_table._rows[str(data_sample_row.id)] = data_sample_row

        state = self._prev_state
        try:
            now = time.perf_counter()
            result = observations_table.any(self.expression)
            capability_label = self.capability_name or self.__class__.__name__

            # Get current frame_id from stream
            frame_id = None
            if stream.frames and len(stream.frames) > 0:
                frame_ids = list(stream.frames.keys())
                if frame_ids:
                    frame_id = frame_ids[-1]

            logger.info(
                "%s ---> evaluates to %s",
                self.expression,
                result,
                extra={
                    "stream_id": stream.stream_id,
                    "capability_name": capability_label,
                    "frame_id": frame_id,
                },
            )

            if result:
                self._last_true_trigger = time.perf_counter()
                state = True
            elif (self._last_true_trigger is not None) and ((now - self._last_true_trigger) > self.patience):
                state = False

            self._entity_buffer.clear()
            self._prev_state = state
            observations_table.clear()

        except Exception as exc:
            # Rate-limit error logging to avoid spam
            stream_id = getattr(stream, "stream_id", "unknown")
            error_key = f"{stream_id}:{type(exc).__name__}"
            self._evaluation_error_count[error_key] += 1

            # Log on first occurrence, then every Nth frame (if configured)
            # When log_errors_every_n_frames=0, always log
            should_log = (
                self.log_errors_every_n_frames == 0
                or self._evaluation_error_count[error_key] == 1
                or self._evaluation_error_count[error_key] % self.log_errors_every_n_frames == 0
            )

            if should_log:
                logger.warning(
                    "RuleTrigger evaluation failed for '%s' (count: %d): %s",
                    self.expression,
                    self._evaluation_error_count[error_key],
                    exc,
                )

        return state


TriggerUnion = Annotated[Union[PeriodicTrigger, RuleTrigger], Field(discriminator="type")]
