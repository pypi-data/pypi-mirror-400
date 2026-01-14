"""Jinja2 rendering utilities."""

import re
from markupsafe import Markup
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, BaseLoader

from zerojs.forms import render_form


class ShadowDOMLoader(FileSystemLoader):
    """Custom loader that wraps .shadow.html components in Declarative Shadow DOM."""

    def get_source(self, environment: Environment, template: str) -> tuple[str, str | None, callable]:
        """Load template and wrap .shadow.html files in Shadow DOM."""
        source, filename, uptodate = super().get_source(environment, template)

        # Check if this is a shadow component
        if template.endswith(".shadow.html"):
            source = self._wrap_in_shadow_dom(template, source)

        return source, filename, uptodate

    def _wrap_in_shadow_dom(self, template: str, source: str) -> str:
        """Wrap component content in Declarative Shadow DOM."""
        # Extract component name: card.shadow.html -> pf-card
        name = template.replace(".shadow.html", "").replace("/", "-").replace("_", "-")
        tag_name = f"pf-{name}"

        return f"""<{tag_name}>
    <template shadowrootmode="open">
{source}
    </template>
</{tag_name}>"""


def _make_pyscript_head(settings: dict[str, Any]) -> callable:
    """Create the pyscript_head() template function."""

    def pyscript_head() -> Markup:
        """Generate PyScript head tags for templates."""
        if not settings.get("PYSCRIPT_ENABLED", False):
            return Markup("")

        version = settings.get("PYSCRIPT_VERSION", "2025.10.1")

        return Markup(f"""<link rel="stylesheet" href="https://pyscript.net/releases/{version}/core.css">
    <script type="module" src="https://pyscript.net/releases/{version}/core.js"></script>""")

    return pyscript_head


class Renderer:
    """Renders HTML templates using Jinja2."""

    # Framework's built-in templates directory
    FRAMEWORK_TEMPLATES = Path(__file__).parent / "templates"

    def __init__(
        self,
        pages_dir: Path,
        components_dir: Path,
        errors_dir: Path | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        self.pages_dir = pages_dir
        self.components_dir = components_dir
        self.errors_dir = errors_dir
        self._settings = settings or {}

        # Create Jinja2 environment with multiple search paths
        # User paths first (higher priority), framework templates last (fallback)
        search_paths = []
        if pages_dir.exists():
            search_paths.append(str(pages_dir))
        if components_dir.exists():
            search_paths.append(str(components_dir))
        if errors_dir and errors_dir.exists():
            search_paths.append(str(errors_dir))

        # Add framework templates as fallback
        if self.FRAMEWORK_TEMPLATES.exists():
            search_paths.append(str(self.FRAMEWORK_TEMPLATES))

        # If no paths exist yet, use current directory as fallback
        if not search_paths:
            search_paths.append(".")

        self.env = Environment(
            loader=ShadowDOMLoader(search_paths),
            autoescape=True,
        )

        # Register global functions
        self.env.globals["pyscript_head"] = _make_pyscript_head(self._settings)
        self.env.globals["render_form"] = render_form

    def render(self, template_path: Path, context: dict[str, Any] | None = None) -> str:
        """Render a template with the given context."""
        # Get template name relative to pages_dir
        relative_path = template_path.relative_to(self.pages_dir)
        template = self.env.get_template(str(relative_path))
        return template.render(context or {})

    def render_file(self, file_path: Path, context: dict[str, Any] | None = None) -> str:
        """Render an arbitrary file with the given context."""
        template = self.env.get_template(file_path.name)
        return template.render(context or {})

    def render_component(self, component_path: Path, context: dict[str, Any] | None = None) -> str:
        """Render a component file with the given context."""
        template = self.env.get_template(component_path.name)
        return template.render(context or {})
