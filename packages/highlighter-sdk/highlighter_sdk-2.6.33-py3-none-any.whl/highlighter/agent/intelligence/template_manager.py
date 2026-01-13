"""Template management for LLM capability."""

from jinja2.sandbox import SandboxedEnvironment

__all__ = ["TemplateManager"]


class TemplateManager:
    """Manages Jinja2 templates with compilation caching

    Compiles templates once at startup, renders many times during
    execution. Provides custom filters for common template tasks.
    """

    def __init__(self, use_jinja2: bool = True, validate: bool = True):
        self.use_jinja2 = use_jinja2
        self.validate = validate
        self.jinja_env = SandboxedEnvironment() if use_jinja2 else None
        self.compiled_templates = {}

        if use_jinja2:
            self._register_filters()

    def _register_filters(self):
        """Register custom Jinja2 filters"""
        self.jinja_env.filters["format_bbox"] = self._format_bbox
        self.jinja_env.filters["bbox_area"] = self._bbox_area

    @staticmethod
    def _format_bbox(annotation) -> str:
        """Format bounding box as [xmin, ymin, xmax, ymax]

        Args:
            annotation: Annotation or observation with location

        Returns:
            String representation of bounding box
        """
        if hasattr(annotation, "location") and annotation.location:
            loc = annotation.location
            return f"[{loc.xmin}, {loc.ymin}, {loc.xmax}, {loc.ymax}]"
        # Handle dict-based annotation (from ObservationsTable rows)
        if isinstance(annotation, dict) and "location" in annotation:
            loc = annotation["location"]
            return f"[{loc['xmin']}, {loc['ymin']}, {loc['xmax']}, {loc['ymax']}]"
        return "None"

    @staticmethod
    def _bbox_area(annotation) -> int:
        """Calculate bounding box area

        Args:
            annotation: Annotation or observation with location

        Returns:
            Area in pixels
        """
        if hasattr(annotation, "location") and annotation.location:
            return annotation.location.area
        # Handle dict-based annotation
        if isinstance(annotation, dict) and "location" in annotation:
            loc = annotation["location"]
            width = loc["xmax"] - loc["xmin"]
            height = loc["ymax"] - loc["ymin"]
            return width * height
        return 0

    def compile(self, template: str, name: str) -> None:
        """Compile and cache a template

        Args:
            template: Template string to compile
            name: Name for this template (e.g., 'prompt', 'system')

        Raises:
            ValueError: If template compilation fails
        """
        if not self.use_jinja2:
            self.compiled_templates[name] = template
            return

        try:
            compiled = self.jinja_env.from_string(template)
            self.compiled_templates[name] = compiled
        except Exception as e:
            raise ValueError(f"Template compilation failed for '{name}': {e}")

    def render(self, name: str, context: any) -> str:
        """Render a compiled template

        Args:
            name: Name of template to render
            context: Context object for template rendering

        Returns:
            Rendered template string

        Raises:
            KeyError: If template not compiled
        """
        if name not in self.compiled_templates:
            raise KeyError(f"Template '{name}' not compiled")

        template = self.compiled_templates[name]

        if not self.use_jinja2:
            # Backward compatibility - simple placeholder replacement
            # Try to get content from context
            if hasattr(context, "frames") and len(context.frames) > 0:
                content = str(context.frames[0].content)
            else:
                content = str(context)
            return template.replace("{{PLACEHOLDER}}", content)

        return template.render(context=context)

    def validate_template(self, name: str, dummy_context: any) -> bool:
        """Validate template with test context

        Args:
            name: Name of template to validate
            dummy_context: Test context for validation

        Returns:
            True if validation successful

        Raises:
            ValueError: If validation fails
        """
        if not self.validate:
            return True

        try:
            self.render(name, dummy_context)
            return True
        except Exception as e:
            raise ValueError(f"Template validation failed for '{name}': {e}")
