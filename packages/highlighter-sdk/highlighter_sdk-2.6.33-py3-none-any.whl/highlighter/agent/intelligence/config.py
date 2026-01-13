"""Configuration classes for LLM capability."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from highlighter.agent.capabilities.base_capability import Capability

__all__ = [
    "LLMProfile",
    "VisionConfig",
    "MonitoringConfig",
    "OutputConfig",
    "LLMInitParameters",
    "LLMStreamParameters",
]


class LLMProfile(str, Enum):
    """Pre-configured profiles for common scenarios"""

    SIMPLE = "simple"  # Text-only processing
    VISION = "vision"  # Vision + observations
    STRUCTURED = "structured"  # JSON/Entity output
    CONVERSATION = "conversation"  # Multi-turn dialogue


class VisionConfig(BaseModel):
    """Vision processing settings"""

    enabled: bool = True
    max_images_per_request: int = 5
    resize_images: bool = True
    max_image_dimension: int = 1568
    image_quality: int = 85
    preserve_format: bool = True  # PNG for alpha channel


class MonitoringConfig(BaseModel):
    """Cost tracking and rate limiting"""

    track_metrics: bool = True
    max_requests_per_minute: int = 60
    max_cost_per_stream: Optional[float] = None


class OutputConfig(BaseModel):
    """Output format configuration"""

    format: str = "text"  # 'text', 'json', 'entities'
    create_entities: bool = False
    schema_version: str = "v1"


class LLMInitParameters(Capability.InitParameters):
    """Initialization parameters for LLM capability"""

    # Core configuration (3-5 parameters)
    profile: LLMProfile = LLMProfile.SIMPLE
    model: str = "claude-3-5-sonnet-20241022"
    prompt_template: Optional[str] = None
    system_prompt_template: Optional[str] = None

    # Frame windowing and taxonomy
    frame_window_size: Optional[int] = None
    time_window_seconds: Optional[float] = None
    taxonomy: Optional[dict] = None  # Will be converted to TaxonomyConfig
    content_filters: Optional[list] = None  # Will be converted to List[ContentFilterConfig]

    # Optional advanced configuration
    vision: Optional[VisionConfig] = None
    monitoring: Optional[MonitoringConfig] = None
    output: Optional[OutputConfig] = None

    # Advanced options
    use_jinja2: bool = True
    validate_template: bool = True
    completion_kwargs: dict = Field(default_factory=dict)
    mock_response: bool = False
    num_retries: int = 8

    # Legacy compatibility
    cache_system_prompt: bool = False

    @model_validator(mode="after")
    def apply_profile_defaults(self) -> "LLMInitParameters":
        """Apply profile-specific defaults"""
        if self.profile == LLMProfile.SIMPLE:
            if self.vision is None:
                self.vision = VisionConfig(enabled=False)
        elif self.profile == LLMProfile.VISION:
            if self.vision is None:
                self.vision = VisionConfig(enabled=True)
            if self.monitoring is None:
                self.monitoring = MonitoringConfig(track_metrics=True)
        elif self.profile == LLMProfile.STRUCTURED:
            if self.output is None:
                self.output = OutputConfig(format="json")
        elif self.profile == LLMProfile.CONVERSATION:
            if self.monitoring is None:
                self.monitoring = MonitoringConfig(track_metrics=True)

        # Set defaults for None configs
        self.vision = self.vision or VisionConfig()
        self.monitoring = self.monitoring or MonitoringConfig()
        self.output = self.output or OutputConfig()
        return self

    @model_validator(mode="after")
    def validate_config_consistency(self) -> "LLMInitParameters":
        """Validate configuration consistency"""
        if self.vision.enabled and not self._model_supports_vision(self.model):
            raise ValueError(
                f"Model {self.model} does not support vision. "
                "Set vision.enabled=False or use a vision model."
            )

        if self.output.format == "entities":
            self.output.create_entities = True

        # Ensure at least one window size is set, default to frame_window_size=1
        if self.frame_window_size is None and self.time_window_seconds is None:
            self.frame_window_size = 1

        # Validate window sizes if set
        if self.frame_window_size is not None and self.frame_window_size < 1:
            raise ValueError("frame_window_size must be at least 1")
        if self.time_window_seconds is not None and self.time_window_seconds <= 0:
            raise ValueError("time_window_seconds must be greater than 0")

        return self

    @staticmethod
    def _model_supports_vision(model: str) -> bool:
        """Check if model supports vision"""
        vision_models = [
            "claude-3",
            "gpt-4o",
            "gpt-4-turbo",
            "gemini-1.5",
            "gemini-pro-vision",
        ]
        return any(vm in model.lower() for vm in vision_models)


class LLMStreamParameters(LLMInitParameters):
    """Per-stream parameters"""

    prompt_template_path: Optional[str] = None
    system_prompt_template_path: Optional[str] = None
    template_vars: dict = Field(default_factory=dict)

    # Conversation config (state in stream.variables)
    enable_conversation: bool = False
    max_history_turns: int = 10

    # Legacy compatibility
    strategy: Optional[str] = None
