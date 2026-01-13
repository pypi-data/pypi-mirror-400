"""
Data payload writers for various content types.

Write Modes:
-----------
Writers support different modes depending on the output format:

Streaming (incremental) writes:
    Data is written incrementally as it arrives, minimizing memory usage.
    Supported by: VideoWriter (for video formats like MP4, AVI)
    Use when: Processing long-duration content or continuous data streams

Batch (buffered) writes:
    All data is buffered in memory before encoding.
    Required by: Formats that need the complete dataset (e.g., ImageWriter for
    multi-image grids, EntityWriter for Avro aggregation)
    Use when: Data size is manageable or format requires full dataset upfront

Note: Not all writers support streaming. Check individual writer documentation
for supported modes.
"""

import io
import logging
import math
import os
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import BinaryIO, Iterable, Union

import av
import numpy as np
from PIL import Image

from highlighter.agent.utilities import EntityAggregator, FileAvroEntityWriter
from highlighter.client import ENTITY_AVRO_SCHEMA
from highlighter.client.base_models.entities import Entities
from highlighter.core.data_models.data_sample import DataSample
from highlighter.io.base import PayloadWriter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EncodeSettings:
    codec: str = "h264"
    pix_fmt: str = "yuv420p"
    crf: int = 23
    preset: str = "medium"
    scenecut: str = "0"


@dataclass
class StreamingState:
    """State for streaming video writes.

    Encapsulates all stateful information needed for incremental video encoding.
    """

    container: av.container.Container | None = None
    stream: av.stream.Stream | None = None
    sink: BinaryIO | None = None
    close_sink: bool = False
    width: int | None = None
    height: int | None = None
    is_open: bool = False

    def reset(self) -> None:
        """Reset all state to initial values."""
        self.container = None
        self.stream = None
        self.sink = None
        self.close_sink = False
        self.width = None
        self.height = None
        self.is_open = False


class ImageWriter(PayloadWriter):
    """
    Serialise one or many image samples as a single **PNG**.

    * If exactly one sample is supplied, the payload is just that image.
    * If more than one sample is supplied, the images are tiled into a
      square-ish grid:  ``cols = ceil(sqrt(N)), rows = ceil(N/cols)``.
    """

    def __init__(self, *, mode: str = "RGB", extension: str = "PNG"):
        """
        Parameters
        ----------
        mode
            PIL/Pillow image mode for the final canvas (defaults to ``"RGB"``).
        extension
            PIL/Pillow image extension for the final canvas. Required if `write`ing
            to a `sink` of type `BinaryIO`. If `sink` is a `str` or `os.PathLike`
            then `extension is ignored. (defaults to ``"PNG"``).


        """
        self.mode = mode
        self.extension = extension

    # The signature mirrors VideoWriter so DataFile.save_local can treat every
    # writer uniformly.
    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        samples = list(samples)
        if not samples:
            raise ValueError("ImageWriter.write() received no samples")

        # Convert every DataSample → PIL.Image
        pil_images = []
        for s in samples:
            if isinstance(s.content, Image.Image):
                img = s.content.convert(self.mode)
            else:
                arr = s.to_ndarray()
                if arr.ndim == 2:  # greyscale → RGB
                    arr = np.stack([arr] * 3, axis=-1)
                img = Image.fromarray(arr).convert(self.mode)
            pil_images.append(img)

        # Tile if necessary
        if len(pil_images) == 1:
            final_img = pil_images[0]
        else:
            w, h = pil_images[0].size
            n = len(pil_images)
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
            canvas = Image.new(self.mode, (cols * w, rows * h))
            for idx, img in enumerate(pil_images):
                r, c = divmod(idx, cols)
                canvas.paste(img.resize((w, h)), (c * w, r * h))
            final_img = canvas

        # Write to the requested sink
        if isinstance(sink, (str, Path)):
            with open(sink, "wb") as f:
                final_img.save(f)
        else:
            final_img.save(sink, format=self.extension)


class TextWriter(PayloadWriter):
    def write():
        pass


class EntityWriter(PayloadWriter):
    def __init__(self, *, extension: str = "avro"):
        """
        Parameters
        ----------
        extension
            file extension which defaults to avro
        """
        self.extension = extension

    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        """
        Encode all Entities into *sink*
        """
        writer = FileAvroEntityWriter(
            ENTITY_AVRO_SCHEMA,
            sink,
        )
        agg = EntityAggregator(
            minimum_track_frame_length=3,
            minimum_embedding_in_track_frame_length=3,
            writer=writer,
        )
        samples = list(samples)
        for sample in samples:
            if not isinstance(sample.content, Entities):
                raise ValueError("EntityWriter requires Entities sample content")
            agg.append_entities(list(sample.content))
        agg.write()


class VideoWriter(PayloadWriter):
    """
    Stream-encode frames into a video sink with efficient, C-based resizing.

    Features:
      • Configurable frame_rate, bit_rate, resolution
      • Pre-flight probing for resolution and bitrate
      • `av.VideoFrame.reformat` for on-the-fly scaling (fast C)
      • Supports both batch and streaming write modes

    Write Modes:
    -----------
    Streaming mode (incremental writes):
        Write frames one at a time to minimize memory usage. Ideal for
        long-running video captures where frames arrive continuously.

        Usage:
            with VideoWriter(frame_rate=24.0) as writer:
                writer.open(sink_path, first_sample)
                for sample in samples:
                    writer.write_frame(sample)
                # Automatically closes on exit

    Batch mode (buffer all samples):
        Buffer all frames in memory then encode. Simpler API for small videos
        or when all frames are already in memory.

        Usage:
            writer = VideoWriter(frame_rate=24.0)
            writer.write(samples, sink_path)

    When to use which mode:
    ----------------------
    - Use streaming: Long-duration videos or continuous captures to minimize memory
    - Use batch: Short videos where all frames fit comfortably in memory
    """

    supports_resize = True

    def __init__(
        self,
        *,
        frame_rate: float = 24.0,
        bit_rate: int | None = None,
        resolution: tuple[int, int] | None = None,
        extension: str = "mp4",
        settings: EncodeSettings = EncodeSettings(),
    ):
        self.frame_rate = frame_rate
        self.bit_rate = bit_rate
        self.resolution = resolution
        self.settings = settings
        self.extension = extension

        # Streaming state encapsulated in dataclass
        self._state = StreamingState()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures container is closed."""
        if self._state.is_open:
            self.close()
        return False

    def _prepare(self, first_frame: DataSample) -> tuple[int, int]:
        """
        Determine target width/height and estimate bit_rate if unset.
        """
        arr = first_frame.to_ndarray()
        h, w = arr.shape[:2]
        if self.resolution:
            width, height = self.resolution
        else:
            width, height = w, h
        if self.bit_rate is None:
            raw_bytes = arr.nbytes
            # use 25% of raw size as heuristic
            self.bit_rate = int(raw_bytes * self.frame_rate * 8 * 0.25)
        return width, height

    def open(
        self,
        sink: Union[str, os.PathLike, BinaryIO],
        first_frame: DataSample,
    ) -> None:
        """
        Open the video container for streaming writes.

        Parameters
        ----------
        sink : Union[str, os.PathLike, BinaryIO]
            Output destination for the video
        first_frame : DataSample
            First frame to determine video properties (resolution, bitrate)

        Raises
        ------
        RuntimeError
            If container is already open
        """
        if self._state.is_open:
            raise RuntimeError("VideoWriter is already open. Call close() first.")

        # Prepare dimensions and bitrate from first frame
        self._state.width, self._state.height = self._prepare(first_frame)

        # Open sink and container with proper cleanup on error
        opened_sink = None
        try:
            if isinstance(sink, (str, Path)):
                opened_sink = open(sink, "wb")
                self._state.sink = opened_sink
                self._state.close_sink = True
            else:
                self._state.sink = sink
                self._state.close_sink = False

            # Open container
            self._state.container = av.open(self._state.sink, mode="w", format=self.extension)

            # Set metadata from first frame's recorded_at if available
            if hasattr(first_frame, "recorded_at") and first_frame.recorded_at is not None:
                first_frame_time = first_frame.recorded_at
                # ISO standard creation time (container level)
                self._state.container.metadata["creation_time"] = first_frame_time.isoformat()
                # QuickTime standard creation date
                self._state.container.metadata["©day"] = first_frame_time.isoformat()
                # Custom field for application-specific queries
                self._state.container.metadata["recorded_at"] = first_frame_time.isoformat()

            # Add stream
            self._state.stream = self._state.container.add_stream(
                self.settings.codec, rate=Fraction(self.frame_rate)
            )
            self._state.stream.width, self._state.stream.height = self._state.width, self._state.height
            self._state.stream.pix_fmt = self.settings.pix_fmt
            self._state.stream.options.update(
                {
                    "crf": str(self.settings.crf),
                    "preset": self.settings.preset,
                    "scenecut": self.settings.scenecut,
                }
            )
            if self.bit_rate:
                self._state.stream.bit_rate = self.bit_rate

            logger.debug(
                f"video writer: {self._state.stream.width}x{self._state.stream.height}, bitrate: {self._state.stream.bit_rate}, pix_fmt: {self._state.stream.pix_fmt}, options: {self._state.stream.options}"
            )
            # Set metadata at track level too
            if hasattr(first_frame, "recorded_at") and first_frame.recorded_at is not None:
                self._state.stream.metadata["creation_time"] = first_frame.recorded_at.isoformat()
                self._state.stream.metadata["recorded_at"] = first_frame.recorded_at.isoformat()
                self._state.stream.metadata["©day"] = first_frame.recorded_at.isoformat()

            self._state.is_open = True
        except Exception:
            if opened_sink:
                opened_sink.close()
            # Reset state to ensure the writer can be safely discarded or reused.
            self._state.reset()
            raise

    def write_frame(self, frame: DataSample) -> None:
        """
        Write a single frame to the video stream.

        Parameters
        ----------
        frame : DataSample
            Frame to encode and write

        Raises
        ------
        RuntimeError
            If container is not open. Call open() first.
        TypeError
            If frame content is not a NumPy ndarray
        """
        if not self._state.is_open:
            raise RuntimeError("VideoWriter is not open. Call open() first.")

        arr = frame.to_ndarray()
        if not isinstance(arr, np.ndarray):
            raise TypeError(f"Expected a NumPy ndarray, got {type(arr).__name__}")

        vf = av.VideoFrame.from_ndarray(arr, format="rgb24")
        # fast, C-level reformat for scaling/pad
        if (vf.width, vf.height) != (self._state.width, self._state.height):
            vf = vf.reformat(width=self._state.width, height=self._state.height, format="rgb24")

        # Encode and mux packets
        for packet in self._state.stream.encode(vf):
            self._state.container.mux(packet)

    def close(self) -> None:
        """
        Flush encoder and close the video container.

        Safe to call multiple times - will only close once.
        """
        if not self._state.is_open:
            return

        # Flush encoder
        for packet in self._state.stream.encode():
            self._state.container.mux(packet)

        # Close container
        self._state.container.close()

        # Close sink if we opened it
        if self._state.close_sink and self._state.sink is not None:
            self._state.sink.close()

        # Reset state
        self._state.reset()

    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        """
        Encode all frames into *sink*, streaming scaled frames via C.

        This method now uses the streaming API internally, avoiding the need
        to load all frames into memory at once.
        """
        # Convert to iterator to peek at first frame
        samples_iter = iter(samples)

        try:
            first_frame = next(samples_iter)
        except StopIteration:
            raise ValueError("VideoWriter.write() received no samples")

        # Use streaming API to avoid loading all frames into memory
        self.open(sink, first_frame)
        try:
            # Write first frame
            self.write_frame(first_frame)

            # Write remaining frames
            for frame in samples_iter:
                self.write_frame(frame)
        finally:
            self.close()
