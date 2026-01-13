import logging
import os
import queue
import shutil
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Callable, Iterator, List, Optional, Union
from urllib.parse import urlparse
from uuid import UUID

from sqlmodel import Session

from highlighter.cli.cli_logging import format_timing
from highlighter.client import HLClient, assessments
from highlighter.client.gql_client import get_threadsafe_hlclient
from highlighter.core.data_models.data_file import DataFile
from highlighter.core.data_models.data_sample import DataSample
from highlighter.core.enums import ContentTypeEnum
from highlighter.core.shutdown import runtime_stop_event

if TYPE_CHECKING:
    from highlighter.client.tasks import ProcessorState

# sentinel used to tell the worker "no more DataFiles coming"
_STOP = object()


class RecorderWorkerFailedError(RuntimeError):
    """Raised when the recorder worker thread has failed and cannot be restarted.

    This indicates that the recorder can no longer save data samples, typically
    because the background worker thread has died and exceeded the maximum restart
    attempts. When this error is raised, the system should handle it appropriately,
    such as by shutting down or switching to a fallback mode.

    Attributes
    ----------
    restart_attempts : int
        The number of times a restart was attempted.
    max_restarts : int
        The maximum configured number of restart attempts.
    lost_samples : int
        The number of samples in the buffer that were lost.
    """

    def __init__(self, *, restart_attempts: int, max_restarts: int, lost_samples: int):
        self.restart_attempts = restart_attempts
        self.max_restarts = max_restarts
        self.lost_samples = lost_samples
        message = (
            f"Recorder worker thread has failed and cannot be restarted after "
            f"{restart_attempts} restart attempts (max: {max_restarts}). "
            f"Unable to save {lost_samples} buffered samples. Recording is no longer possible."
        )
        super().__init__(message)


class RecordMode(str, Enum):
    OFF = "off"  # stream only, no persistence
    OUTPUT_FOLDER = "output_folder"  #
    LOCAL = "local"  # DataFile.save_local() only
    CLOUD = "cloud"  # DataFile.save_to_cloud() only
    BOTH = "both"  # local + CLOUD


class RecordingState(str, Enum):
    OFF = "off"  # recording disabled, behaves as if RecordMode is OFF
    ON = "on"  # recording active, follows configured RecordMode


def _validate_enum(value, enum_class, param_name: str):
    """Validate and convert enum parameter."""
    if isinstance(value, str):
        try:
            return enum_class(value.lower())
        except ValueError:
            allowed = ", ".join(m.value for m in enum_class)
            raise ValueError(f"{param_name} must be one of {{{allowed}}}")
    elif isinstance(value, enum_class):
        return value
    else:
        allowed = ", ".join(m.value for m in enum_class)
        raise ValueError(f"{param_name} must be one of {{{allowed}}}")


class Recorder:
    """
    Wraps *any* iterator that yields `DataSamples` and optionally groups and saves
    them into `DataFiles`. Supports custom output locations and filename templates
    with built-in security protections against path traversal attacks.

    Parameters
    ----------
    iterator : Iterator[DataSample]
        Source of samples (e.g., VideoReader).
    record : RecordMode, default "off"
        Enable/disable on-the-fly persistence.
        - "off": Stream only, no persistence
        - "local": Save files locally using DataFile.save_local()
        - "cloud": Save files to cloud using DataFile.save_to_cloud()
        - "both": Save files both locally and to cloud
    recording_state : RecordingState, default "on"
        Controls whether recording is currently active. This allows dynamic
        control over recording behavior at runtime:
        - "off": Recording disabled, behaves as if RecordMode is OFF regardless
          of the configured record mode
        - "on": Recording active, follows the configured RecordMode
        Can be changed at runtime using set_recording_state() method.
    session_factory : Callable[[], Session] | None
        Factory function that returns SQLModel sessions – required when `record != "off"`.
    data_source_uuid, account_uuid : UUID | None
        Stored in the generated `DataFile`s (required when `record != "off"`).
    samples_per_file : int | None, default None
        How many samples per `DataFile`. When this threshold is reached,
        a new DataFile is created and saved. Mutually exclusive with `seconds_per_file`.
        If neither `samples_per_file` nor `seconds_per_file` is specified, defaults to 20.0 seconds.

        **Memory Usage**: Samples are buffered in memory until this threshold is reached,
        then written to disk. To reduce memory usage, use a smaller value (e.g., 30-60 samples
        for video). The VideoWriter uses streaming encoding, so frames are encoded and written
        incrementally without loading all frames into memory at once.

    seconds_per_file : float | None, default None
        Duration in seconds per `DataFile`. When the elapsed time between the first
        sample in the current batch and the current sample exceeds this threshold,
        a new DataFile is created and saved. Mutually exclusive with `samples_per_file`.
        Time is calculated using the `recorded_at` timestamp of each DataSample.

        **Memory Usage**: Similar to `samples_per_file`, samples are buffered until the
        time threshold is reached. To reduce memory usage, use a smaller duration (e.g., 5-10
        seconds for video). The VideoWriter uses streaming encoding for efficient memory usage.
    writer_opts : dict | None
        Additional options passed to `DataFile.save_local()` (e.g., {"frame_rate": 24.0}).
    content_type : str, default `ContentTypeEnum.IMAGE`
        `DataFile.content_type` to use when persisting.
    enforce_unique_files : bool, default False
        If True, prevents saving files with duplicate hashes.
    use_streaming_writes : bool, default True
        Enable streaming writes for video content to minimize memory usage. When enabled,
        video frames are written to disk incrementally as they arrive, rather than buffering
        all frames in memory. Only applies to VIDEO content type; other content types always use buffering.

        Set to False to use traditional buffering mode (only needed for custom writers that
        don't support the streaming API).
    queue_size : int, default 8
        Maximum number of DataFiles queued for background processing.
    data_file_id : UUID | None, default None
        Optional specific UUID for the first DataFile. If None, auto-generated.
    output_folder : Path | str | None, default None
        Custom folder path for saving additional file copies. If provided, files are
        copied to this location after normal save. If None with output_filename_template,
        uses current working directory. Supports "." to explicitly specify current
        directory. Security: Path traversal attempts are blocked.
    output_filename_template : str | None, default None
        Template for generating custom filenames with variable substitution.
        If None, uses default filename pattern. Files are copied to the custom
        location after normal DataFile save operation.

        Available template variables:
        - {file_id}: DataFile UUID
        - {timestamp}: Full timestamp (YYYYMMDD_HHMMSS)
        - {date}: Date only (YYYYMMDD)
        - {time}: Time only (HHMMSS)
        - {year}, {month}, {day}: Individual date components
        - {hour}, {minute}, {second}: Individual time components
        - {extension}: File extension

        Examples:
        - "video_{timestamp}" → "video_20241201_143022.mp4"
        - "{year}/{month}/capture_{file_id}" → "2024/12/capture_abc123.mp4"
        - "data_{date}_{time}.{extension}" → "data_20241201_143022.mp4"
        - ".hidden_{timestamp}" → ".hidden_20241201_143022.mp4" (hidden files)
        - "backup_{date}.tar.gz" → "backup_20241201.tar.gz.mp4" (complex extensions)
        - "logs/{year}/{month}/.daily_log" → "logs/2024/12/.daily_log.mp4" (nested + hidden)

        Security: Templates are sanitized to prevent path traversal attacks.
        Invalid characters are removed, ".." sequences are blocked, but legitimate
        dots in filenames (extensions, hidden files) are preserved.

    Examples
    --------
    Basic usage with default settings:

    >>> processor = Recorder(
    ...     iterator=video_reader,
    ...     record=RecordMode.LOCAL,
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=uuid.uuid4(),
    ...     account_uuid=uuid.uuid4(),
    ... )

    Custom output location and filename template:

    >>> processor = Recorder(
    ...     iterator=video_reader,
    ...     record=RecordMode.LOCAL,
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=uuid.uuid4(),
    ...     account_uuid=uuid.uuid4(),
    ...     output_folder="/data/exports",
    ...     output_filename_template="{year}/{month}/video_{timestamp}",
    ... )

    Organized folder structure with date-based organization:

    >>> processor = Recorder(
    ...     iterator=image_reader,
    ...     record=RecordMode.BOTH,  # Save locally and to cloud
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=uuid.uuid4(),
    ...     account_uuid=uuid.uuid4(),
    ...     output_folder="/exports",
    ...     output_filename_template="{year}/{month}/{day}/batch_{timestamp}_{file_id}",
    ...     samples_per_file=100,
    ... )

    Time-based chunking with seconds_per_file:

    >>> # Create 30-second video chunks
    >>> processor = Recorder(
    ...     iterator=video_reader,
    ...     record=RecordMode.LOCAL,
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=uuid.uuid4(),
    ...     account_uuid=uuid.uuid4(),
    ...     seconds_per_file=30.0,  # 30 seconds per file
    ...     output_folder="/data/chunks",
    ...     output_filename_template="chunk_{timestamp}",
    ...     writer_opts={"frame_rate": 24.0},
    ... )

    Complete workflow example:

    >>> # 1. Set up data source
    >>> video_reader = VideoReader(
    ...     source_url="/data/video.mp4",
    ...     sample_fps=12,
    ... )
    >>>
    >>> # 2. Configure processor with custom output
    >>> processor = Recorder(
    ...     iterator=video_reader,
    ...     record=RecordMode.LOCAL,
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=data_source_id,
    ...     account_uuid=account_id,
    ...     samples_per_file=25,
    ...     output_folder="/data/processed",
    ...     output_filename_template="video_{date}_{time}",
    ...     writer_opts={"frame_rate": 24.0},
    ... )
    >>>
    >>> # 3. Process samples
    >>> for sample in processor:
    ...     # Process each sample (ML inference, analysis, etc.)
    ...     process_sample(sample)
    >>>
    >>> # 4. Ensure all data is saved
    >>> processor.flush()
    >>>
    >>> # 5. Access saved files
    >>> for data_file in processor.saved_files:
    ...     print(f"Saved: {data_file.original_source_url}")

    Dynamic Recording Control:

    >>> # Set up processor with recording initially OFF
    >>> processor = Recorder(
    ...     iterator=video_reader,
    ...     record=RecordMode.LOCAL,  # Configure mode but don't start recording
    ...     recording_state=RecordingState.OFF,  # Initially disabled
    ...     session_factory=lambda: Session(engine),
    ...     data_source_uuid=uuid.uuid4(),
    ...     account_uuid=uuid.uuid4(),
    ... )
    >>>
    >>> # Process some samples without recording
    >>> for i, sample in enumerate(processor):
    ...     if i == 100:  # Start recording after 100 samples
    ...         processor.set_recording_state(RecordingState.ON)
    ...     elif i == 500:  # Stop recording after 500 samples
    ...         processor.set_recording_state(RecordingState.OFF)
    ...     # Process sample...
    >>>
    >>> # Check current state
    >>> print(f"Recording state: {processor.recording_state}")
    >>>
    >>> # Final flush to save any remaining buffered data
    >>> processor.flush()

    Security Notes
    --------------
    The custom output functionality includes built-in security protections:

    - **Path Traversal Prevention**: Templates like "../../../etc/passwd" are sanitized
    - **Character Sanitization**: Invalid filename characters are removed or replaced
    - **Path Validation**: Destination paths are validated to stay within base directories
    - **Subdirectory Support**: Safe creation of nested folder structures

    All file operations are logged for security auditing.
    """

    def __init__(
        self,
        *,
        iterator: Iterator[DataSample],
        record: RecordMode = RecordMode.OFF,
        recording_state: RecordingState = RecordingState.ON,
        session_factory: Optional[Callable[[], Session]] = None,
        data_source_uuid: Optional[UUID] = None,
        account_uuid: Optional[UUID] = None,
        samples_per_file: Optional[int] = None,
        seconds_per_file: Optional[float] = None,
        writer_opts: Optional[dict] = None,
        content_type: str = ContentTypeEnum.IMAGE,
        queue_size: int = 8,
        enforce_unique_files: bool = False,
        data_file_id: Optional[UUID] = None,
        output_folder: Optional[Union[Path, str]] = None,
        output_filename_template: Optional[str] = None,
        stream_id: Optional[str] = None,
        capability_name: Optional[str] = None,
        use_streaming_writes: bool = True,
    ):
        self._stop_event = runtime_stop_event or threading.Event()
        self.logger = logging.getLogger(__name__)
        self._flush_attempted = False
        self._stream_id = stream_id
        self._capability_name = capability_name

        # Diagnostic logging for stream_id
        if stream_id is None or stream_id == "":
            import traceback

            self.logger.warning(
                "Recorder created with stream_id=%r, capability_name=%r. Call stack:\n%s",
                stream_id,
                capability_name,
                "".join(traceback.format_stack()[:-1]),
            )
        else:
            self.logger.debug(
                "Recorder created with stream_id=%r, capability_name=%r",
                stream_id,
                capability_name,
            )

        record = _validate_enum(record, RecordMode, "record")
        recording_state = _validate_enum(recording_state, RecordingState, "recording_state")

        if record != RecordMode.OFF:
            if session_factory is None:
                raise ValueError("session_factory required when record ≠ 'off'")
            if (record != RecordMode.LOCAL) and (data_source_uuid is None or account_uuid is None):
                raise ValueError("data_source_uuid and account_uuid are required")

        if samples_per_file is not None and seconds_per_file is not None:
            raise ValueError("Cannot specify both samples_per_file and seconds_per_file")
        elif samples_per_file is None and seconds_per_file is None:
            seconds_per_file = 20.0

        self._record_mode: RecordMode = record  # save enum
        self._recording_state: RecordingState = recording_state
        self._recording_state_lock = Lock()  # guard access to recording state
        self._active_processor_state: Optional["ProcessorState"] = None
        self._save_local = record in (RecordMode.LOCAL, RecordMode.BOTH)
        self._save_cloud = record in (RecordMode.CLOUD, RecordMode.BOTH)

        self._iterator = iterator
        self._record = record
        self._session_factory = session_factory
        self._data_source_uuid = data_source_uuid
        self._account_uuid = account_uuid
        self._samples_per_file = samples_per_file
        self._seconds_per_file = seconds_per_file
        self._writer_opts = writer_opts or {}
        self._content_type = content_type
        self._enforce_unique_files = enforce_unique_files
        self._output_folder = Path(output_folder) if output_folder else None
        self._output_filename_template = output_filename_template
        self._use_streaming_writes = use_streaming_writes

        # batching state (only used if record=True)
        self._buffer: List[DataSample] = []
        self._saved_ids: List[UUID] = []
        self._saved_lock = Lock()  # guard cross-thread writes

        # Streaming write state (for video content)
        self._streaming_writer = None  # Open VideoWriter instance
        self._streaming_file_path = None  # Path to file being written
        self._streaming_sample_count = 0  # Number of samples written to current file

        # background worker setup
        self._q: queue.Queue[DataFile | object] = queue.Queue(maxsize=queue_size)
        self._worker_exception: Optional[Exception] = None
        self._flush_attempted = False
        self._worker_restart_count = 0
        self._max_worker_restarts = 3
        self._worker_loop_submission_responce_queues = {}

        self._assessment = None
        self._current_data_file_id = uuid.uuid4() if data_file_id is None else data_file_id

        self._recording_start = None
        self._batch_start = None
        self._batch_end = None
        self._stream_batch_start_frame_index = 0  # current buffer's starting stream frame id

        if self._record_mode is not RecordMode.OFF:
            if self._record_mode in (RecordMode.CLOUD, RecordMode.BOTH):
                self.hl_client = HLClient.get_client()
            self._start_worker()
        else:
            self._worker = None

    def __iter__(self):
        return self

    def __next__(self) -> DataSample:
        try:
            sample = next(self._iterator)
            sample.data_file_id = self._current_data_file_id

        except StopIteration:
            self.flush()  # ← guarantees clean shutdown
            raise  # ← propagate to caller

        # Check if recording should be active (both RecordMode != OFF and RecordingState == ON)
        with self._recording_state_lock:
            recording_active = (
                self._record_mode is not RecordMode.OFF and self._recording_state == RecordingState.ON
            )

        self.logger.debug(f"Recording active: {self._content_type} {recording_active}")
        if recording_active:
            if self._recording_start is None:
                self._recording_start = sample.recorded_at  # TODO: or datetime.now()

            if self._batch_start is None:
                self._batch_start = sample.recorded_at  # TODO: or datetime.now()

            # Update batch_end with each new sample
            self._batch_end = sample.recorded_at

            current_sample_time = None
            if self._seconds_per_file is not None:
                current_sample_time = sample.recorded_at or datetime.now(tz=timezone.utc)

            # Check if we should use streaming writes for video
            use_streaming = self._use_streaming_writes and self._content_type == ContentTypeEnum.VIDEO

            # Check if we should flush BEFORE adding the current sample
            should_flush = False

            # Sample count threshold
            if self._samples_per_file is not None:
                count_to_check = self._streaming_sample_count if use_streaming else len(self._buffer)
                if self._samples_per_file > 0 and count_to_check >= self._samples_per_file:
                    should_flush = True

            # Duration threshold
            elif self._seconds_per_file is not None and (self._buffer or self._streaming_sample_count > 0):
                # Only check duration if buffer is not empty or streaming writer is active
                elapsed = (current_sample_time - self._batch_start).total_seconds()
                if elapsed >= self._seconds_per_file:
                    should_flush = True

            if should_flush:
                self._stream_batch_start_frame_index = sample.stream_frame_index
                self._flush_buffer_async(self._active_processor_state)
                self._batch_start = current_sample_time

            # Set media_frame_index correctly for the current data file chunk
            sample.media_frame_index = sample.stream_frame_index - self._stream_batch_start_frame_index

            if use_streaming:
                # Streaming mode: write frame immediately to disk
                if self._streaming_writer is None:
                    self._open_streaming_writer(sample)

                # Write frame immediately
                self._streaming_writer.write_frame(sample)
                self._streaming_sample_count += 1

                # Keep lightweight reference in buffer (for metadata only)
                # Clear the heavy frame data since it's already written to disk
                cloned = sample.model_copy(deep=False)
                cloned.content = None  # Drop the numpy array to free memory
                self._buffer.append(cloned)
            else:
                # Traditional buffering mode
                cloned = sample.model_copy(deep=False)
                self._buffer.append(cloned)

        return sample

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        return False  # Don’t suppress exceptions from user code

    def __del__(self):
        # Only attempt flush if we haven't already tried and failed
        if not self._flush_attempted:
            try:
                self.flush()
            except Exception:
                # Never raise exceptions from __del__ as it can cause issues
                # But we should log them as warnings so they're visible
                import logging
                import traceback

                logging.getLogger(__name__).warning(
                    "Exception during flush in __del__:\n%s", traceback.format_exc()
                )

    def start_recording(self, submission, processor_state: "ProcessorState"):
        processor_state.processor = self
        processor_state.submission = submission
        processor_state.pending_chunks = 0
        processor_state.stopping = False
        processor_state.finished = False
        processor_state.error = None

        self._active_processor_state = processor_state
        with self._recording_state_lock:
            self._recording_state = RecordingState.ON

    def stop_recording(self, processor_state: Optional["ProcessorState"] = None):
        state = processor_state or self._active_processor_state
        with self._recording_state_lock:
            self._recording_state = RecordingState.OFF

        if state is not None:
            state.stopping = True

        # If we have buffered samples, flush them
        if self._buffer:
            # Flush current buffer to create a truncated file
            self._flush_buffer_async(state)
        elif state is not None and state.pending_chunks == 0:
            state.finished = True

        if state is not None and state.finished:
            self._active_processor_state = None

    @property
    def recording_state(self) -> RecordingState:
        """Get the current recording state."""
        with self._recording_state_lock:
            return self._recording_state

    def clear_completed_recording(self, processor_state: "ProcessorState"):
        """Called by TaskContext when a submission is finalized."""
        if self._active_processor_state is processor_state:
            self._active_processor_state = None

    def flush(self, join_timeout: float = 10.0):
        """
        Persist any residual samples, block until background saves complete,
        and propagate worker exceptions.

        join_timeout - timeout when joining the worker thread
        """
        self._flush_attempted = True
        if self._record_mode is RecordMode.OFF:
            return

        if self._buffer:
            self._flush_buffer_async()

        # Best-effort, non-blocking STOP sentinel
        enqueued_stop = False
        try:
            self._q.put_nowait(_STOP)
            enqueued_stop = True
        except queue.Full:
            # brief retry window (optional)
            deadline = time.time() + 2.0
            while time.time() < deadline:
                try:
                    self._q.put(_STOP, timeout=0.2)
                    enqueued_stop = True
                    break
                except queue.Full:
                    pass
            if not enqueued_stop:
                self.logger.warning(
                    "flush(): queue full; proceeding without STOP sentinel",
                    extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                )

        if self._worker is not None:
            self._worker.join(timeout=join_timeout)
            if self._worker.is_alive():
                self.logger.error(
                    "flush(): worker still alive after %.1fs (qsize=%s)",
                    join_timeout,
                    getattr(self._q, "qsize", lambda: "?")(),
                    extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                )

        if self._worker_exception:
            raise self._worker_exception  # re-raise in caller thread

    @property
    def saved_files(self) -> List[DataFile]:
        """
        Return a fresh list of DataFile instances re-loaded from the database,
        so their column attributes are fully populated and won’t try to lazy-load
        on a closed session.
        """
        with self._saved_lock:
            if self._record_mode is RecordMode.OFF or not self._saved_ids:
                return []

            ids_snapshot = list(self._saved_ids)

        if not ids_snapshot:
            return []

        with self._session_factory() as session:
            files = []
            for id in ids_snapshot:
                df = session.get(DataFile, id)
                if df:
                    files.append(df)

        # ensure private attribute _data_dir exists so that get_data_dir() works
        for df in files:
            # Guarantee the pydantic-private storage exists
            priv = getattr(df, "__pydantic_private__", None)
            if priv is None:
                object.__setattr__(df, "__pydantic_private__", {})
                priv = df.__pydantic_private__  # type: ignore[attr-defined]

            # Initialise _data_dir slot if absent
            if "_data_dir" not in priv:
                priv["_data_dir"] = None

        return files

    def _start_worker(self):
        """Start the background worker thread."""
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="RecorderWorker",
            daemon=True,
        )
        self._worker.start()
        self.logger.info(
            f"Started worker thread (restart count: {self._worker_restart_count})",
            extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
        )

    def _check_worker_health(self):
        """Check if worker thread is alive and restart if necessary."""
        if self._worker is None or self._worker.is_alive():
            return True

        # Worker has died - check if we've already exceeded restart limit
        if self._worker_restart_count >= self._max_worker_restarts:
            self.logger.error(
                f"Worker thread died and max restarts ({self._max_worker_restarts}) exceeded. "
                f"Current restart count: {self._worker_restart_count}. Will not restart worker.",
                extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
            )
            return False

        # Log the worker death and increment restart count
        self._worker_restart_count += 1
        self.logger.warning(
            f"Worker thread died (restart {self._worker_restart_count}/{self._max_worker_restarts}). "
            f"Attempting to restart...",
            extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
        )

        # Clear any previous exception to avoid re-raising stale errors
        if self._worker_exception:
            self.logger.warning(
                f"Clearing previous worker exception: {self._worker_exception}",
                extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
            )
            self._worker_exception = None

        # Restart the worker
        self._start_worker()
        return True

    def _generate_filename(self, file_id: UUID, extension: str, recorded_at: datetime) -> str:
        """Generate filename using template or default pattern.

        Parameters
        ----------
        file_id : UUID
            Unique identifier for the file
        extension : str
            File extension (without dot)
        recorded_at : datetime
            Timestamp when the data was recorded

        Returns
        -------
        str
            Generated filename with template variables substituted

        Raises
        ------
        ValueError
            If template contains invalid variables

        Examples
        --------
        >>> # With template "video_{timestamp}_{file_id}"
        >>> filename = processor._generate_filename(
        ...     UUID('123e4567-e89b-12d3-a456-426614174000'),
        ...     'mp4',
        ...     datetime(2024, 12, 1, 14, 30, 22)
        ... )
        >>> print(filename)  # "video_20241201_143022_123e4567-e89b-12d3-a456-426614174000.mp4"
        """
        if self._output_filename_template is None:
            return f"{file_id}.{extension}"

        source_url = getattr(self._iterator, "source_url", None)
        if source_url is not None:
            source_filename = Path(urlparse(source_url, scheme="file").path).stem
        else:
            source_filename = ""

        # Available template variables
        template_vars = {
            "file_id": str(file_id),
            "timestamp": recorded_at.strftime("%Y%m%d_%H%M%S"),
            "date": recorded_at.strftime("%Y%m%d"),
            "time": recorded_at.strftime("%H%M%S"),
            "year": recorded_at.strftime("%Y"),
            "month": recorded_at.strftime("%m"),
            "day": recorded_at.strftime("%d"),
            "hour": recorded_at.strftime("%H"),
            "minute": recorded_at.strftime("%M"),
            "second": recorded_at.strftime("%S"),
            "extension": extension,
            "source_filename": source_filename,
        }

        try:
            filename = self._output_filename_template.format(**template_vars)
            # Ensure the extension is included if not in template
            if not filename.endswith(f".{extension}"):
                filename = f"{filename}.{extension}"
            return filename
        except KeyError as e:
            raise ValueError(
                f"Invalid template variable: {e}. Available variables: {list(template_vars.keys())}"
            )

    def _get_output_directory(self) -> Path:
        """Get the output directory for custom file copies.

        Returns
        -------
        Path
            Output directory path. Uses custom output_folder if specified,
            otherwise defaults to current working directory.

        Notes
        -----
        This method determines where custom file copies will be placed when
        using output_folder or output_filename_template parameters. The directory
        is created automatically during the copy operation.
        """
        if self._output_folder is not None:
            return self._output_folder
        # Default to current working directory when custom filename template is used
        return Path.cwd()

    def _open_streaming_writer(self, first_sample: DataSample):
        """Open a streaming video writer for incremental frame writes.

        Parameters
        ----------
        first_sample : DataSample
            The first sample to determine video properties
        """
        from highlighter.io.registry import get_writer

        # Get writer with options
        writer = get_writer(self._content_type, **self._writer_opts)

        # Create a temporary DataFile to get the correct data directory
        # This avoids cross-filesystem moves when flushing
        temp_df = DataFile(
            file_id=self._current_data_file_id,
            account_uuid=self._account_uuid or uuid.uuid4(),
            data_source_uuid=self._data_source_uuid or uuid.uuid4(),
            content_type=self._content_type,
        )
        data_dir = temp_df.get_data_dir()

        # Create temp file in the same directory as the final destination
        # This ensures the move/rename is a cheap operation on the same filesystem
        os.makedirs(data_dir, exist_ok=True)
        temp_path = data_dir / f"{self._current_data_file_id}.tmp.{writer.extension}"

        # Open the writer in streaming mode
        self._streaming_writer = writer
        self._streaming_writer.open(temp_path, first_sample)
        self._streaming_file_path = temp_path
        self._streaming_sample_count = 0

        self.logger.debug(f"Opened streaming writer: {temp_path}")

    def _close_streaming_writer(self):
        """Close the currently open streaming writer."""
        if self._streaming_writer is not None:
            self._streaming_writer.close()
            self.logger.debug(f"Closed streaming writer: {self._streaming_file_path}")
            self._streaming_writer = None
            # Keep path for DataFile to use

    def _flush_buffer_async(self, processor_state: Optional["ProcessorState"] = None):
        """Move current buffer into a new DataFile and queue it to worker.

        Raises
        ------
        RecorderWorkerFailedError
            If the worker thread is dead and cannot be restarted after
            exceeding the maximum restart attempts.
        """
        # Check worker health before queuing
        if not self._check_worker_health():
            num_samples = len(self._buffer)
            self._buffer = []  # Clear buffer to prevent memory buildup
            # Clean up streaming writer if open
            if self._streaming_writer is not None:
                try:
                    self._close_streaming_writer()
                    if self._streaming_file_path and self._streaming_file_path.exists():
                        self._streaming_file_path.unlink()
                except Exception as e:
                    self.logger.error(f"Error cleaning up streaming writer: {e}")
                self._streaming_file_path = None
                self._streaming_sample_count = 0

            exc = RecorderWorkerFailedError(
                restart_attempts=self._worker_restart_count,
                max_restarts=self._max_worker_restarts,
                lost_samples=num_samples,
            )
            self.logger.error(str(exc))
            raise exc

        # Close streaming writer if active
        prewritten_file_path = None
        if self._streaming_writer is not None:
            self._close_streaming_writer()
            prewritten_file_path = self._streaming_file_path
            self._streaming_file_path = None
            self._streaming_sample_count = 0

        # Calculate recorded_until by adding last frame duration for video content
        recorded_until = self._batch_end
        if self._content_type == ContentTypeEnum.VIDEO and self._batch_end is not None:
            # Get frame rate from writer_opts (e.g., {"frame_rate": 24.0})
            frame_rate = self._writer_opts.get("frame_rate") or self._writer_opts.get("fps")
            if frame_rate and frame_rate > 0:
                from datetime import timedelta

                frame_duration_seconds = 1.0 / frame_rate
                recorded_until = self._batch_end + timedelta(seconds=frame_duration_seconds)

        df = DataFile(
            file_id=self._current_data_file_id,
            account_uuid=self._account_uuid or uuid.uuid4(),
            data_source_uuid=self._data_source_uuid or uuid.uuid4(),
            content_type=self._content_type,
            enforce_unique_files=self._enforce_unique_files,
            recorded_at=self._batch_start,
            recorded_until=recorded_until,
        )
        df.add_samples(self._buffer)
        self._buffer = []  # reset for next batch
        self._batch_end = None
        self._current_data_file_id = uuid.uuid4()

        try:
            state = processor_state or self._active_processor_state
            if state is not None:
                state.pending_chunks += 1
            queue_start = time.perf_counter()
            self._q.put(
                (df, state, prewritten_file_path), timeout=5.0
            )  # may block if queue is full, Add timeout to prevent hanging
            queue_elapsed = time.perf_counter() - queue_start
            timing_queue = format_timing(
                "queue_put", queue_elapsed, color_threshold={"fast": 0.1, "slow": 1.0}
            )
            self.logger.debug(
                f"queue size: {self._q.qsize()}, {timing_queue}",
                extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
            )
        except queue.Full:
            self.logger.error("Worker queue is full. Dropping DataFile to prevent blocking.")
            # Clean up prewritten file if it exists
            if prewritten_file_path and prewritten_file_path.exists():
                try:
                    prewritten_file_path.unlink()
                except Exception as e:
                    self.logger.error(f"Error removing prewritten file: {e}")
            # Could optionally save directly to local file as emergency fallback

    def _copy_to_custom_location(self, data_file: DataFile):
        """Copy the saved file to custom location with security protections.

        This method creates additional copies of DataFiles in custom locations
        when output_folder or output_filename_template parameters are specified.
        The original file remains in its standard location.

        Parameters
        ----------
        data_file : DataFile
            The DataFile that has been saved and should be copied

        Security Features
        ----------------
        - **Path Traversal Prevention**: Sanitizes filenames to prevent "../" attacks
        - **Path Validation**: Ensures destination stays within allowed directories
        - **Character Sanitization**: Removes dangerous filename characters
        - **Safe Directory Creation**: Creates nested directories securely

        Notes
        -----
        - Files are copied after normal DataFile save operation
        - Creates destination directories as needed (including nested structures)
        - Logs all copy operations for audit trails
        - Silently returns if no custom output parameters are configured
        - On errors, logs warnings but does not interrupt main processing
        """
        if self._output_folder is None and self._output_filename_template is None:
            return  # No custom location specified

        # Get source file path
        source_path = data_file.path_to_content_file
        if not source_path.exists():
            self.logger.warning(f"Source file does not exist: {source_path}")
            return

        # Determine base destination directory
        base_dest_dir = self._get_output_directory()

        if self._output_filename_template is not None:
            # Extract extension from source file
            extension = source_path.suffix[1:]  # Remove the dot
            # Generate custom filename
            custom_filename = self._generate_filename(
                data_file.file_id, extension, data_file.recorded_at or datetime.now()
            )

            # Security: Sanitize the filename to prevent path traversal
            # Remove any path separators and resolve any relative path components
            sanitized_filename = self._sanitize_filename(custom_filename)
            dest_path = base_dest_dir / sanitized_filename
        else:
            dest_path = base_dest_dir / source_path.name

        # Security: Ensure the destination path is within the base directory
        try:
            resolved_dest = dest_path.resolve()
            resolved_base = base_dest_dir.resolve()

            # Check if the resolved destination is within the base directory
            # Use is_relative_to for Python 3.9+ or manual check for older versions
            try:
                # Python 3.9+
                if not resolved_dest.is_relative_to(resolved_base):
                    self.logger.error(f"Path traversal attempt detected: {dest_path}")
                    return
            except AttributeError:
                # Fallback for older Python versions
                if not str(resolved_dest).startswith(str(resolved_base)):
                    self.logger.error(f"Path traversal attempt detected: {dest_path}")
                    return
        except Exception as e:
            self.logger.error(f"Failed to validate destination path {dest_path}: {e}")
            return

        # Create all necessary parent directories
        try:
            os.makedirs(dest_path.parent, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create destination directory {dest_path.parent}: {e}")
            return

        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.info(
                f"Copied file from {source_path} to {dest_path}",
                extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
            )
        except Exception as e:
            self.logger.error(
                f"Failed to copy file from {source_path} to {dest_path}: {e}",
                extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
            )

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal and invalid characters.

        This method provides comprehensive filename sanitization to prevent security
        vulnerabilities while preserving legitimate subdirectory structures.

        Parameters
        ----------
        filename : str
            Raw filename or path from template expansion

        Returns
        -------
        str
            Sanitized filename safe for filesystem operations

        Security Protections
        -------------------
        - Removes parent directory references (".." sequences)
        - Blocks sequences of only dots ("...", "..", ".") as potential traversal attempts
        - Strips dangerous filename characters (<>:"|?*\\)
        - Filters out empty path components
        - Provides fallback for completely invalid input

        Functionality
        -------------
        - Preserves legitimate subdirectory structures (e.g., "2024/12/file.txt")
        - Maintains alphanumeric characters, hyphens, underscores, dots, spaces
        - Supports nested folder organization via forward slashes
        - Preserves file extensions (e.g., ".txt", ".tar.gz", ".backup.zip")
        - Allows hidden files (e.g., ".hidden", ".env", ".gitignore")
        - Supports complex naming patterns with legitimate dots

        Examples
        --------
        >>> processor._sanitize_filename("../../../etc/passwd")
        'etc/passwd'

        >>> processor._sanitize_filename("2024/12/01/video<>.mp4")
        '2024/12/01/videomp4'

        >>> processor._sanitize_filename("valid_file-name.txt")
        'valid_file-name.txt'

        >>> processor._sanitize_filename("...///.../malicious")
        'malicious'

        >>> processor._sanitize_filename("<>:\"|?*\\")
        'sanitized_file'
        """
        # Remove or replace potentially dangerous characters
        # Allow forward slashes for subdirectory support, but sanitize path components
        path_parts = []
        for part in Path(filename).parts:
            # Skip dangerous directory references (before any other processing)
            if part in (".", ".."):
                continue

            # Remove leading/trailing whitespace
            sanitized_part = part.strip()

            # Skip empty parts
            if not sanitized_part:
                continue

            # Remove sequences of only dots (potential traversal attempts)
            # Allow legitimate filenames with dots but block suspicious patterns
            if sanitized_part.replace(".", "") == "":
                # Part consists only of dots - skip it as potentially dangerous
                continue

            # Remove or replace invalid filename characters
            # Keep alphanumeric, hyphens, underscores, dots, and spaces
            sanitized_part = "".join(c for c in sanitized_part if c.isalnum() or c in "-_. ")

            # Ensure the part is not empty after sanitization
            if sanitized_part:
                path_parts.append(sanitized_part)

        if not path_parts:
            # Fallback to a safe default if all parts were removed
            return "sanitized_file"

        return str(Path(*path_parts))

    def _worker_loop(self):
        """
        Receives DataFile objects, opens its *own* SQLModel Session, writes
        them to disk (and cloud), then marks task done.  Stores first
        exception encountered.
        """
        hl_client = None
        session: Optional[Session] = None
        try:
            if self._record_mode in (RecordMode.CLOUD, RecordMode.BOTH):
                hl_client = get_threadsafe_hlclient(self.hl_client.api_token, self.hl_client.endpoint_url)

            while True:
                try:
                    result = self._q.get(timeout=0.5)  # TODO: what is the best timeout? use global?
                except queue.Empty:
                    if self._stop_event.is_set():
                        break
                    continue  # loop and check stop_event again

                if result is _STOP:
                    break  # clean exit

                # Unpack result - may include prewritten file path
                if isinstance(result, tuple) and len(result) == 3:
                    data_file, processor_state, prewritten_file_path = result
                else:
                    # Backward compatibility: handle old format
                    data_file, processor_state = result
                    prewritten_file_path = None

                try:
                    if session is None:
                        session = self._session_factory()  # lazy open
                    samples_length = data_file.samples_length()

                    # Handle individual DataFile processing with isolated error handling
                    self._process_data_file(
                        data_file,
                        session,
                        samples_length,
                        hl_client if self._record_mode in (RecordMode.CLOUD, RecordMode.BOTH) else None,
                        processor_state,
                        prewritten_file_path,
                    )

                    # Only add to saved list if processing succeeded
                    with self._saved_lock:
                        self._saved_ids.append(data_file.file_id)

                except Exception as e:
                    # Log the error but continue processing other files
                    self.logger.error(
                        f"Failed to process DataFile {data_file.file_id}: {e}\n{traceback.format_exc()}"
                    )
                    if processor_state is not None:
                        processor_state.error = e
                    # Don't add to saved_ids since processing failed
                    raise

                finally:
                    if processor_state is not None:
                        processor_state.pending_chunks -= 1
                        if (
                            processor_state.error is None
                            and processor_state.stopping
                            and processor_state.pending_chunks == 0
                        ):
                            processor_state.finished = True
                    self._q.task_done()

        except Exception as exc:
            self.logger.error(
                "Exception in worker thread [%s]: %s\n%s",
                threading.current_thread().name,
                str(exc),
                traceback.format_exc(),
            )
            self._worker_exception = exc

        finally:
            # done – commit & close
            if session is not None:
                try:
                    session.close()
                except Exception as e:
                    self.logger.warning(f"Error closing session: {e}")

            if hl_client is not None:
                try:
                    hl_client.close()
                except Exception as e:
                    self.logger.warning(f"Error closing HLClient in recorder worker: {e}")

    def _process_data_file(
        self,
        data_file: DataFile,
        session: Session,
        samples_length: int,
        hl_client=None,
        processor_state: Optional["ProcessorState"] = None,
        prewritten_file_path: Optional[Path] = None,
    ):
        """Process a single DataFile with proper error handling.

        Parameters
        ----------
        data_file : DataFile
            The data file to process
        session : Session
            Database session
        samples_length : int
            Number of samples in the file
        hl_client : HLClient, optional
            Client for cloud operations
        processor_state : ProcessorState, optional
            State object for tracking recording progress
        prewritten_file_path : Path, optional
            Path to prewritten file (for streaming writes)
        """
        process_start = time.perf_counter()
        match self._record_mode:
            case RecordMode.OFF:
                # Should never reach worker when OFF, but keep for completeness
                pass

            case RecordMode.LOCAL:
                save_start = time.perf_counter()
                data_file.save_local(
                    session,
                    writer_opts=self._writer_opts,
                    stream_id=self._stream_id,
                    capability_name=self._capability_name,
                    prewritten_file_path=prewritten_file_path,
                )
                save_elapsed = time.perf_counter() - save_start

                timing_save = format_timing(
                    "save_local", save_elapsed, color_threshold={"fast": 0.5, "slow": 2.0}
                )
                mode_info = "(streaming)" if prewritten_file_path else "(buffered)"
                self.logger.info(
                    f'DataFile("{data_file.file_id}")#save_local {samples_length} samples to {data_file.path_to_content_file} in {timing_save}',
                    extra={
                        "stream_id": self._stream_id,
                        "capability_name": self._capability_name,
                        "mode": mode_info,
                    },
                )

            case RecordMode.OUTPUT_FOLDER:
                save_start = time.perf_counter()
                data_file.save_local(
                    session,
                    writer_opts=self._writer_opts,
                    stream_id=self._stream_id,
                    capability_name=self._capability_name,
                    prewritten_file_path=prewritten_file_path,
                )
                save_elapsed = time.perf_counter() - save_start

                copy_start = time.perf_counter()
                # After successful save, copy to custom location if specified
                self._copy_to_custom_location(data_file)
                copy_elapsed = time.perf_counter() - copy_start

                # After successful copy, remove local copy only if custom output was specified
                if self._output_folder is not None or self._output_filename_template is not None:
                    try:
                        os.remove(data_file.path_to_content_file)
                    except FileNotFoundError:
                        self.logger.warning("Local file already removed: %s", data_file.path_to_content_file)

                mode_info = "(streaming)" if prewritten_file_path else "(buffered)"
                self.logger.info(
                    f'DataFile("{data_file.file_id}")#save_local {mode_info} {save_elapsed:.3f}s, copy {copy_elapsed:.3f}s'
                )

            case RecordMode.CLOUD:
                save_start = time.perf_counter()
                data_file.save_local(
                    session,
                    writer_opts=self._writer_opts,
                    stream_id=self._stream_id,
                    capability_name=self._capability_name,
                    prewritten_file_path=prewritten_file_path,
                )
                save_elapsed = time.perf_counter() - save_start
                try:
                    file_size_bytes = data_file.path_to_content_file.stat().st_size
                    file_size_mb = file_size_bytes / (1024 * 1024)
                except Exception as e:
                    file_size_bytes = 0
                    file_size_mb = 0.0
                    self.logger.warning(f"Could not get file size: {e}")

                try:
                    upload_start = time.perf_counter()
                    _saved_data_file: "ImageType" = data_file.save_to_cloud(session, hl_client=hl_client)
                    upload_elapsed = time.perf_counter() - upload_start

                    # Calculate upload bitrate
                    if upload_elapsed > 0:
                        upload_mbps = (file_size_bytes * 8) / (
                            upload_elapsed * 1_000_000
                        )  # Megabits per second
                        upload_mb_per_sec = file_size_mb / upload_elapsed  # Megabytes per second
                    else:
                        upload_mbps = 0.0
                        upload_mb_per_sec = 0.0

                    if processor_state is not None:
                        assessments.append_data_files_to_not_finalised_assessment(
                            hl_client,
                            processor_state.submission,
                            [_saved_data_file],
                        )

                        # Log after successful append
                        recorded_at = data_file.recorded_at.isoformat() if data_file.recorded_at else "N/A"
                        self.logger.info(
                            f"Appended DataFile to submission: "
                            f"case_id={processor_state.case_id}, "
                            f"submission_id={processor_state.submission.id}, "
                            f"data_file_id={data_file.file_id}, "
                            f"recorded_at={recorded_at}, "
                            f"samples={samples_length}",
                            extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                        )

                    timing_save = format_timing(
                        "save_local", save_elapsed, color_threshold={"fast": 0.5, "slow": 2.0}
                    )
                    timing_upload = format_timing(
                        "upload", upload_elapsed, color_threshold={"fast": 1.0, "slow": 5.0}
                    )

                    self.logger.info(
                        f'DataFile("{data_file.file_id}")#save_to_cloud '
                        f"({samples_length} samples, {file_size_mb:.2f} MB) "
                        f"{timing_save}, {timing_upload} "
                        f"({upload_mb_per_sec:.2f} MB/s, {upload_mbps:.2f} Mbps) "
                        f"queue: {self._q.qsize()}",
                        extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                    )

                    # After successful upload, remove local copy
                    try:
                        os.remove(data_file.path_to_content_file)
                    except FileNotFoundError:
                        self.logger.warning("Local file already removed: %s", data_file.path_to_content_file)

                except ValueError as e:
                    # Handle cloud upload errors gracefully to allow recovery
                    error_msg = str(e)
                    try:
                        file_path = data_file.path_to_content_file
                    except (ValueError, AttributeError):
                        file_path = "<unknown path>"

                    # Log the error with stream context
                    self.logger.error(
                        f"Cloud upload failed for DataFile {data_file.file_id}: {error_msg}. "
                        f"File: {file_path}",
                        extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                    )

                    # Keep local file for debugging and continue processing
                    # Don't re-raise - allow the worker to continue with next file
                    if processor_state is not None:
                        processor_state.pending_chunks -= 1

            case RecordMode.BOTH:
                save_start = time.perf_counter()
                data_file.save_local(
                    session,
                    writer_opts=self._writer_opts,
                    stream_id=self._stream_id,
                    capability_name=self._capability_name,
                    prewritten_file_path=prewritten_file_path,
                )
                save_elapsed = time.perf_counter() - save_start

                # Get file size for bitrate calculation
                try:
                    file_size_bytes = data_file.path_to_content_file.stat().st_size
                    file_size_mb = file_size_bytes / (1024 * 1024)
                except Exception as e:
                    file_size_bytes = 0
                    file_size_mb = 0.0
                    self.logger.warning(f"Could not get file size: {e}")

                timing_save = format_timing(
                    "save_local", save_elapsed, color_threshold={"fast": 0.5, "slow": 2.0}
                )
                mode_info = "(streaming)" if prewritten_file_path else "(buffered)"
                self.logger.info(
                    f'DataFile("{data_file.file_id}")#save_local '
                    f"{samples_length} samples ({file_size_mb:.2f} MB) to {data_file.path_to_content_file} in {timing_save}",
                    extra={
                        "stream_id": self._stream_id,
                        "capability_name": self._capability_name,
                        "mode": mode_info,
                    },
                )

                try:
                    upload_start = time.perf_counter()
                    data_file.save_to_cloud(session, hl_client=hl_client)
                    upload_elapsed = time.perf_counter() - upload_start

                    # Calculate upload bitrate
                    if upload_elapsed > 0:
                        upload_mbps = (file_size_bytes * 8) / (
                            upload_elapsed * 1_000_000
                        )  # Megabits per second
                        upload_mb_per_sec = file_size_mb / upload_elapsed  # Megabytes per second
                    else:
                        upload_mbps = 0.0
                        upload_mb_per_sec = 0.0

                    if processor_state is not None:
                        assessments.append_data_files_to_not_finalised_assessment(
                            hl_client,
                            processor_state.submission,
                            [data_file],
                        )

                        # Log after successful append
                        recorded_at = data_file.recorded_at.isoformat() if data_file.recorded_at else "N/A"
                        self.logger.info(
                            f"Appended DataFile to submission: "
                            f"case_id={processor_state.case_id}, "
                            f"submission_id={processor_state.submission.id}, "
                            f"data_file_id={data_file.file_id}, "
                            f"recorded_at={recorded_at}, "
                            f"samples={samples_length}",
                            extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                        )

                    self.logger.info(
                        f'DataFile("{data_file.file_id}")#save_to_cloud '
                        f"({samples_length} samples, {file_size_mb:.2f} MB) "
                        f"upload {upload_elapsed:.3f}s ({upload_mb_per_sec:.2f} MB/s, {upload_mbps:.2f} Mbps) "
                        f"queue: {self._q.qsize()}",
                        extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                    )
                except ValueError as e:
                    # Handle cloud upload errors gracefully to allow recovery
                    error_msg = str(e)
                    try:
                        file_path = data_file.path_to_content_file
                    except (ValueError, AttributeError):
                        file_path = "<unknown path>"

                    # Log the error with stream context
                    self.logger.error(
                        f"Cloud upload failed for DataFile {data_file.file_id}: {error_msg}. "
                        f"File: {file_path}. Local file preserved.",
                        extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
                    )

                    # Keep local file for debugging and continue processing
                    # Don't re-raise - allow the worker to continue with next file
                    if processor_state is not None:
                        processor_state.pending_chunks -= 1

            case _:
                raise ValueError(f"Unhandled RecordMode: {self._record_mode}")

        process_elapsed = time.perf_counter() - process_start
        timing_total = format_timing("total", process_elapsed, color_threshold={"fast": 1.0, "slow": 5.0})
        self.logger.debug(
            f'DataFile("{data_file.file_id}") {timing_total}',
            extra={"stream_id": self._stream_id, "capability_name": self._capability_name},
        )
