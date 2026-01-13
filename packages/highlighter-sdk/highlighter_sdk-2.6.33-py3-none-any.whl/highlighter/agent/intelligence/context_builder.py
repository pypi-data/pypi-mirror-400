"""Unified context builder with frame windowing, taxonomy, and Jinja2 support."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import celpy

from highlighter.agent.observations_table import ObservationsTable
from highlighter.client.base_models.entities import Entities
from highlighter.core.data_models.data_sample import DataSample

__all__ = [
    "ContextBuilder",
    "TaxonomyConfig",
    "ContentFilterConfig",
    "TemplateContext",
    "Frame",
]


@dataclass
class TaxonomyConfig:
    """Taxonomy configuration for context rendering"""

    # Object classes with descriptions
    object_classes: Dict[str, str] = field(default_factory=dict)
    # Attributes with descriptions
    attributes: Dict[str, str] = field(default_factory=dict)
    # Input taxonomy: maps object classes to their input attributes
    input_taxonomy: Dict[str, List[str]] = field(default_factory=dict)
    # Output taxonomy: defines expected output structure
    output_taxonomy: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ContentFilterConfig:
    """Configuration for filtering one specific content type to manage memory

    Each ContentFilterConfig governs buffering for ONE content type (video, audio,
    observations, text). Use multiple configs for different content types flowing
    through the pipeline.

    This prevents memory overflow by controlling what gets added to ContextBuilder.

    Examples:
        # Video stream buffering - HD only, every 5th frame, max 20
        ContentFilterConfig(
            content_type="video",
            filter_expr="width >= 1280 && height >= 720",
            sample_rate=5,
            max_samples=20
        )

        # Image buffering - high-res only, every image, max 10
        ContentFilterConfig(
            content_type="image",
            filter_expr="width >= 1920 && height >= 1080",
            sample_rate=1,
            max_samples=10
        )

        # Audio buffering - every 10th sample, max 10
        ContentFilterConfig(
            content_type="audio",
            sample_rate=10,
            max_samples=10
        )

        # Observations - keep last 50
        ContentFilterConfig(
            content_type="observations",
            max_samples=50
        )

        # Text - include all, no limits
        ContentFilterConfig(
            content_type="text"
        )

    Available CEL fields from DataSample:
        - content_type: str (e.g., "image", "video", "text", "audio")
        - stream_frame_index: int
        - media_frame_index: int
        - recorded_at: timestamp
        - width: int (for image/video)
        - height: int (for image/video)
    """

    # Required: Which content type this filter applies to
    content_type: str

    # Optional CEL expression for advanced filtering
    filter_expr: Optional[str] = None

    # Optional: Sample rate (1 = include all, 5 = every 5th, etc.)
    sample_rate: int = 1

    # Optional: Maximum samples to buffer (if not specified, no limit)
    max_samples: Optional[int] = None

    def __post_init__(self):
        """Initialize counters and compile CEL expression"""
        self._sample_counter: int = 0
        self._total_counter: int = 0

        # Compile CEL expression if provided
        self._cel_program = None
        if self.filter_expr:
            try:
                env = celpy.Environment()
                ast = env.compile(self.filter_expr)
                self._cel_program = env.program(ast)
            except Exception as e:
                raise ValueError(f"Invalid CEL filter expression for '{self.content_type}': {e}")

    def _to_cel_context(self, data_sample: DataSample) -> dict:
        """Convert DataSample to CEL context dict

        Args:
            data_sample: DataSample to convert

        Returns:
            Dictionary for CEL evaluation
        """
        ctx = {
            "content_type": data_sample.content_type,
            "stream_frame_index": data_sample.stream_frame_index,
            "media_frame_index": data_sample.media_frame_index,
            "recorded_at": data_sample.recorded_at,
        }

        # Add width/height for image/video content
        if data_sample.content_type.startswith(("image", "video")) and data_sample.wh:
            ctx["width"] = data_sample.wh[0]
            ctx["height"] = data_sample.wh[1]

        return celpy.json_to_cel(ctx)

    def should_include(self, data_sample: DataSample) -> bool:
        """Determine if a data sample should be included based on filter rules

        Evaluation order:
        1. CEL expression (if provided) - must pass
        2. max_samples limit - must not exceed
        3. sample_rate sampling - determines final inclusion

        Args:
            data_sample: DataSample to check

        Returns:
            True if sample should be included, False otherwise
        """
        # 1. Evaluate CEL expression if provided
        if self._cel_program:
            try:
                ctx = self._to_cel_context(data_sample)
                matches = self._cel_program.evaluate(ctx)
                if not matches:
                    return False
            except (celpy.evaluation.CELEvalError, TypeError, KeyError):
                # If CEL evaluation fails, reject the sample
                return False

        # 2. Check max_samples limit
        if self.max_samples is not None and self._total_counter >= self.max_samples:
            return False

        # 3. Apply sample rate
        self._sample_counter += 1

        if self._sample_counter >= self.sample_rate:
            self._sample_counter = 0
            self._total_counter += 1
            return True

        return False

    def reset(self):
        """Reset counters for next window"""
        self._sample_counter = 0
        self._total_counter = 0


class ContextBuilder:
    """Unified context builder with frame windowing and Jinja2 template support

    Manages memory by buffering different content types (video, audio, observations, text)
    with independent filtering strategies to prevent overflow.

    Features:
    - Frame windowing: Accumulate N frames before processing
    - Time windowing: Accumulate frames over T seconds before processing
    - Per-type buffering: Each content type has its own filter configuration
    - CEL expressions: Advanced filtering per content type
    - Sample rate control: Subsample high-frequency streams
    - Max samples: Cap buffer size per content type
    - Taxonomy support: Domain knowledge for complex use cases
    - Jinja2 templates: Flexible user-defined prompt formatting
    - Observation access: Clean API for entity observations

    Usage:
        # Buffer by frame count with content filters
        builder = ContextBuilder(
            frame_window_size=10,
            content_filters=[
                # Video: HD only, every 5th frame, max 20
                ContentFilterConfig(
                    content_type="video",
                    filter_expr="width >= 1280 && height >= 720",
                    sample_rate=5,
                    max_samples=20
                ),
                # Images: High-res only, every image, max 10
                ContentFilterConfig(
                    content_type="image",
                    filter_expr="width >= 1920 && height >= 1080",
                    sample_rate=1,
                    max_samples=10
                ),
                # Audio: Every 10th sample, max 10
                ContentFilterConfig(
                    content_type="audio",
                    sample_rate=10,
                    max_samples=10
                ),
                # Observations: Keep last 50
                ContentFilterConfig(
                    content_type="observations",
                    max_samples=50
                ),
                # Text: Include all, no limits
                ContentFilterConfig(
                    content_type="text"
                )
            ],
            taxonomy=TaxonomyConfig(...),
            stream_id="stream_123"
        )

        # Buffer by time (5 seconds)
        builder = ContextBuilder(
            time_window_seconds=5.0,
            content_filters=[
                # Video: HD only, every 5th frame, max 20
                ContentFilterConfig(
                    content_type="video",
                    filter_expr="width >= 1280 && height >= 720",
                    sample_rate=5,
                    max_samples=20
                ),
                # Images: High-res only, every image, max 10
                ContentFilterConfig(
                    content_type="image",
                    filter_expr="width >= 1920 && height >= 1080",
                    sample_rate=1,
                    max_samples=10
                ),
                # Audio: Every 10th sample, max 10
                ContentFilterConfig(
                    content_type="audio",
                    sample_rate=10,
                    max_samples=10
                ),
                # Observations: Keep last 50
                ContentFilterConfig(
                    content_type="observations",
                    max_samples=50
                ),
                # Text: Include all, no limits
                ContentFilterConfig(
                    content_type="text"
                )
            ],
            taxonomy=TaxonomyConfig(...),
            stream_id="stream_123"
        )

        # Buffer by both frame and time (whichever comes first)
        builder = ContextBuilder(
            frame_window_size=100,
            time_window_seconds=5.0,
            content_filters=[
                # Video: HD only, every 5th frame, max 20
                ContentFilterConfig(
                    content_type="video",
                    filter_expr="width >= 1280 && height >= 720",
                    sample_rate=5,
                    max_samples=20
                ),
                # Images: High-res only, every image, max 10
                ContentFilterConfig(
                    content_type="image",
                    filter_expr="width >= 1920 && height >= 1080",
                    sample_rate=1,
                    max_samples=10
                ),
                # Audio: Every 10th sample, max 10
                ContentFilterConfig(
                    content_type="audio",
                    sample_rate=10,
                    max_samples=10
                ),
                # Observations: Keep last 50
                ContentFilterConfig(
                    content_type="observations",
                    max_samples=50
                ),
                # Text: Include all, no limits
                ContentFilterConfig(
                    content_type="text"
                )
            ],
            taxonomy=TaxonomyConfig(...),
            stream_id="stream_123"
        )

        # Accumulate frames (filtering applied automatically per content type)
        builder.add_to_context(data_samples, entities)
        builder.add_to_context(data_samples, entities)

        # Build context when window is full
        if builder.is_window_full():
            context = builder.build_context()
            # Use with TemplateManager:
            # rendered = template_manager.render("prompt", context)
            builder.clear()  # Resets all filter counters
    """

    def __init__(
        self,
        frame_window_size: Optional[int] = None,
        time_window_seconds: Optional[float] = None,
        taxonomy: Optional[TaxonomyConfig] = None,
        content_filters: Optional[List[ContentFilterConfig]] = None,
        stream_id: Optional[str] = None,
    ):
        """Initialize ContextBuilder

        Args:
            frame_window_size: Number of frames to accumulate before rendering (default: 1)
            time_window_seconds: Number of seconds to accumulate before rendering (optional)
            taxonomy: Optional taxonomy configuration for domain knowledge
            content_filters: Optional list of per-content-type filter configurations
            stream_id: Optional stream identifier

        Note:
            - If both frame_window_size and time_window_seconds are specified, the window
              is considered full when EITHER condition is met (whichever comes first)
            - If neither is specified, defaults to frame_window_size=1
        """
        # Default to frame_window_size=1 if neither is specified
        if frame_window_size is None and time_window_seconds is None:
            frame_window_size = 1

        self.frame_window_size = frame_window_size
        self.time_window_seconds = time_window_seconds
        self.taxonomy = taxonomy or TaxonomyConfig()
        self.stream_id = stream_id

        # Build lookup dictionary by content_type for fast filtering
        self._filters_by_type: Dict[str, ContentFilterConfig] = {}
        if content_filters:
            for filter_config in content_filters:
                self._filters_by_type[filter_config.content_type] = filter_config

        # Accumulated data
        self._data_samples: List[DataSample] = []
        self._entities_buffer: Entities = Entities()
        self._template_vars: Dict[str, Any] = {}
        self._window_start_time: Optional[datetime] = None

    def add_to_context(
        self,
        data_samples: List[DataSample],
        entities: Optional[Entities] = None,
        template_vars: Optional[Dict[str, Any]] = None,
    ):
        """Add data samples and entities to the context window

        Data samples are filtered according to their content_type filter configuration.
        If no filter exists for a content_type, all samples of that type are included.

        Args:
            data_samples: List of DataSample objects
            entities: Optional dict of entities by ID
            template_vars: Optional custom template variables
        """
        # Apply per-content-type filtering
        filtered_samples = []
        for sample in data_samples:
            # Look up filter for this content type
            content_filter = self._filters_by_type.get(sample.content_type)

            if content_filter:
                # Apply filter if one exists for this content type
                if content_filter.should_include(sample):
                    filtered_samples.append(sample)
            else:
                # No filter for this content type - include by default
                filtered_samples.append(sample)

        # Set window start time on first sample if using time window
        # For multi-stream aggregation, use the earliest timestamp from the first batch
        if self.time_window_seconds is not None and self._window_start_time is None and filtered_samples:
            # Initialize with the earliest timestamp from this first batch
            self._window_start_time = min(sample.recorded_at for sample in filtered_samples)

        self._data_samples.extend(filtered_samples)

        if entities:
            self._entities_buffer.merge(entities, strategy="append")

        if template_vars:
            self._template_vars.update(template_vars)

    def is_window_full(self, current_sample_time: Optional[datetime] = None) -> bool:
        """Check if frame or time window is full

        Args:
            current_sample_time: Optional timestamp of current sample being processed.
                                 Used to check time window even if sample hasn't been added yet.

        Returns:
            True if:
            - frame_window_size is set and accumulated frames >= frame_window_size, OR
            - time_window_seconds is set and time elapsed >= time_window_seconds
            When both are set, returns True if EITHER condition is met.
        """
        # Check frame count condition
        if self.frame_window_size is not None:
            if len(self._data_samples) >= self.frame_window_size:
                return True

        # Check time window condition
        if self.time_window_seconds is not None and self._window_start_time is not None:
            # Use current_sample_time if provided, otherwise find the latest sample in buffer
            if current_sample_time:
                elapsed = (current_sample_time - self._window_start_time).total_seconds()
                if elapsed >= self.time_window_seconds:
                    return True
            elif self._data_samples:
                # Use the latest timestamp across all accumulated samples
                # This handles multi-stream aggregation where samples may arrive out of order
                latest_time = max(sample.recorded_at for sample in self._data_samples)
                elapsed = (latest_time - self._window_start_time).total_seconds()
                if elapsed >= self.time_window_seconds:
                    return True

        return False

    def build_context(self) -> "TemplateContext":
        """Build template context from accumulated data

        Returns:
            TemplateContext object for use with Jinja2 templates
        """

        return TemplateContext(
            data_samples=self._data_samples,
            entities=self._entities_buffer,
            stream_id=self.stream_id or "unknown",
            taxonomy=self.taxonomy,
            custom_vars=self._template_vars,
        )

    def clear(self):
        """Clear accumulated data and reset all content filter counters"""
        self._data_samples.clear()
        self._entities_buffer.clear()
        self._window_start_time = None
        # Keep template_vars and taxonomy (they're configuration)
        # Reset all content filter counters for next window
        for content_filter in self._filters_by_type.values():
            content_filter.reset()

    def get_accumulated_count(self) -> int:
        """Get number of accumulated data samples"""
        return len(self._data_samples)

    def get_data_samples(self) -> List[DataSample]:
        """Get accumulated data samples

        Returns:
            Direct reference to accumulated DataSample list (not a copy)
        """
        return self._data_samples


class TemplateContext:
    """Template context for Jinja2 rendering with full feature support

    Provides access to:
    - Frames (data samples with observations)
    - Taxonomy (object classes, attributes, input/output schemas)
    - Custom variables
    - Observation tables with CEL filtering

    Example template:
        # System Prompt
        You are analyzing {{ context.taxonomy.object_classes | length }} object types.

        # Taxonomy
        {% for class_name, description in context.taxonomy.object_classes.items() %}
        - {{ class_name }}: {{ description }}
        {% endfor %}

        # Frames
        {% for frame in context.frames %}
        Frame {{ frame.index }}: {{ frame.observations | length }} observations
        {% endfor %}

        # High-confidence detections using CEL filtering
        {% set high_conf = context.observations.filter("attribute.object_class.confidence >= 0.8") %}
        {% for obs in high_conf %}
        - {{ obs.attribute.object_class.value.name }}
        {% endfor %}
    """

    def __init__(
        self,
        data_samples: List[DataSample],
        entities: Optional[Entities],
        stream_id: str,
        taxonomy: TaxonomyConfig,
        custom_vars: Dict[str, Any],
    ):
        self._data_samples = data_samples
        self._entities = entities
        self._stream_id = stream_id
        self._taxonomy = taxonomy
        self._custom_vars = custom_vars

        # Lazy-loaded properties
        self._frames = None
        self._observations = None

    @property
    def stream_id(self) -> str:
        """Current stream identifier"""
        return self._stream_id

    @property
    def taxonomy(self) -> TaxonomyConfig:
        """Taxonomy configuration

        Example:
            {% for class_name, desc in context.taxonomy.object_classes.items() %}
            - {{ class_name }}: {{ desc }}
            {% endfor %}
        """
        return self._taxonomy

    @property
    def frames(self) -> List["Frame"]:
        """All frames in the accumulated window

        Example:
            {% for frame in context.frames %}
            Frame {{ frame.index }}: {{ frame.width }}x{{ frame.height }}
            Observations: {{ frame.observations | length }}
            {% endfor %}
        """
        if self._frames is None:
            self._frames = [Frame(ds, self._get_frame_observations(ds)) for ds in self._data_samples]
        return self._frames

    @property
    def observations(self) -> ObservationsTable:
        """All observations across all frames

        Example:
            {% set high_conf = context.observations.filter("attribute.object_class.confidence >= 0.8") %}
            Found {{ high_conf | length }} high-confidence detections

            {% for obs in context.observations.filter("attribute.object_class.value.name == 'person'") %}
            - Person at ({{ obs.annotation.location.xmin }}, {{ obs.annotation.location.ymin }})
            {% endfor %}
        """
        if self._observations is None:
            # Create observations table directly from entities buffer to avoid duplication
            # In multi-stream mode, entities are accumulated across streams/frames, and creating
            # per-frame observation tables would duplicate the same entities multiple times.
            if not self._entities:
                self._observations = ObservationsTable(rows={})
            else:
                # Use the first data sample as reference for data_sample fields in observation rows
                # The actual observation timestamps come from annotation.occurred_at
                reference_sample = self._data_samples[0] if self._data_samples else None
                if reference_sample:
                    self._observations = self._entities.to_observations_table(
                        self._stream_id, reference_sample
                    )
                else:
                    self._observations = ObservationsTable(rows={})
        return self._observations

    @property
    def entities(self) -> Optional[Entities]:
        """Raw entities dictionary

        Provides direct access to all entities aggregated across streams.

        Example:
            {% if context.entities %}
            Total entities: {{ context.entities | length }}
            {% for entity_id, entity in context.entities.items() %}
            Entity {{ entity_id }}:
              - Annotations: {{ entity.annotations | length }}
              - Observations: {% for ann in entity.annotations %}{{ ann.observations | length }}{% endfor %}
            {% endfor %}
            {% endif %}
        """
        return self._entities

    @property
    def observation_rows(self) -> List:
        """All observation rows as a list (for easier template iteration)

        Use this when you want to iterate over all observations without CEL filtering.

        Example:
            {% for obs in context.observation_rows %}
            - {{ obs.attribute_id }}: {{ obs.value }}
            {% endfor %}
        """
        if self._observations is None:
            # Build observations table first
            _ = self.observations
        return list(self._observations._rows.values())

    def __getitem__(self, key: str):
        """Access custom template variables

        Example:
            Task: {{ context['task_description'] }}
        """
        return self._custom_vars.get(key)

    def _get_frame_observations(self, data_sample):
        """Get observations for specific frame"""
        if not self._entities:
            # Return empty ObservationsTable
            return ObservationsTable(rows={})

        obs_table = self._entities.to_observations_table(self._stream_id, data_sample)
        return obs_table


@dataclass
class Frame:
    """Single data sample with observations"""

    _data_sample: DataSample
    _observations_table: ObservationsTable

    @property
    def index(self) -> int:
        """Frame index in stream"""
        return self._data_sample.stream_frame_index

    @property
    def type(self) -> str:
        """Content type (e.g., 'image', 'video', 'text')"""
        return self._data_sample.content_type

    @property
    def timestamp(self):
        """Frame timestamp"""
        return self._data_sample.recorded_at

    @property
    def width(self) -> Optional[int]:
        """Frame width (for image/video)"""
        if self.type.startswith(("image", "video")):
            return self._data_sample.wh[0]
        return None

    @property
    def height(self) -> Optional[int]:
        """Frame height (for image/video)"""
        if self.type.startswith(("image", "video")):
            return self._data_sample.wh[1]
        return None

    @property
    def content(self):
        """Frame content (use with caution in templates)"""
        return self._data_sample.content

    @property
    def observations(self) -> ObservationsTable:
        """Observations for this frame"""
        return self._observations_table
