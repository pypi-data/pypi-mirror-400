"""Tests for Jinja2 renderer."""

from pathlib import Path

import pytest
from jinja2 import TemplateNotFound

from zerojs.renderer import Renderer


class TestRenderTemplateWithContext:
    """Tests for rendering templates with context variables."""

    def test_renders_simple_variable(self, tmp_path: Path) -> None:
        """Template receives and renders context variables."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (pages_dir / "hello.html").write_text("<h1>Hello {{ name }}!</h1>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "hello.html", {"name": "World"})

        assert result == "<h1>Hello World!</h1>"

    def test_renders_multiple_variables(self, tmp_path: Path) -> None:
        """Template can use multiple context variables."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (pages_dir / "user.html").write_text("<p>{{ name }} - {{ email }}</p>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(
            pages_dir / "user.html",
            {"name": "Alice", "email": "alice@example.com"},
        )

        assert result == "<p>Alice - alice@example.com</p>"

    def test_renders_with_conditionals(self, tmp_path: Path) -> None:
        """Template conditionals work with context."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (pages_dir / "status.html").write_text("{% if success %}OK{% else %}FAIL{% endif %}")

        renderer = Renderer(pages_dir, components_dir)

        result_true = renderer.render(pages_dir / "status.html", {"success": True})
        assert result_true == "OK"

        result_false = renderer.render(pages_dir / "status.html", {"success": False})
        assert result_false == "FAIL"

    def test_renders_with_loops(self, tmp_path: Path) -> None:
        """Template loops work with context lists."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (pages_dir / "list.html").write_text("{% for item in items %}{{ item }},{% endfor %}")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "list.html", {"items": ["a", "b", "c"]})

        assert result == "a,b,c,"


class TestRenderComponent:
    """Tests for rendering components."""

    def test_renders_component_with_context(self, tmp_path: Path) -> None:
        """Component renders with provided context."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "button.html").write_text('<button class="{{ variant }}">{{ text }}</button>')

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render_component(
            components_dir / "button.html",
            {"variant": "primary", "text": "Click me"},
        )

        assert result == '<button class="primary">Click me</button>'

    def test_component_without_context(self, tmp_path: Path) -> None:
        """Component renders without context (empty dict)."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "static.html").write_text("<div>Static content</div>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render_component(components_dir / "static.html")

        assert result == "<div>Static content</div>"


class TestTemplateInheritance:
    """Tests for Jinja2 template inheritance."""

    def test_extends_base_template(self, tmp_path: Path) -> None:
        """Child template extends base template."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "base.html").write_text("<html><body>{% block content %}{% endblock %}</body></html>")
        (pages_dir / "child.html").write_text(
            "{% extends 'base.html' %}{% block content %}<h1>Hello</h1>{% endblock %}"
        )

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "child.html")

        assert result == "<html><body><h1>Hello</h1></body></html>"

    def test_multiple_blocks(self, tmp_path: Path) -> None:
        """Child can override multiple blocks."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "base.html").write_text(
            "<title>{% block title %}Default{% endblock %}</title><main>{% block content %}{% endblock %}</main>"
        )
        (pages_dir / "page.html").write_text(
            "{% extends 'base.html' %}"
            "{% block title %}Custom Title{% endblock %}"
            "{% block content %}Content here{% endblock %}"
        )

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "page.html")

        assert "<title>Custom Title</title>" in result
        assert "<main>Content here</main>" in result

    def test_include_component(self, tmp_path: Path) -> None:
        """Template can include components."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "header.html").write_text("<header>Logo</header>")
        (pages_dir / "page.html").write_text("{% include 'header.html' %}<main>Content</main>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "page.html")

        assert result == "<header>Logo</header><main>Content</main>"

    def test_include_with_context(self, tmp_path: Path) -> None:
        """Included component receives context."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "greeting.html").write_text("Hello {{ name }}!")
        (pages_dir / "page.html").write_text("{% include 'greeting.html' %}")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "page.html", {"name": "Alice"})

        assert result == "Hello Alice!"


class TestMissingTemplate:
    """Tests for error handling with missing templates."""

    def test_missing_template_raises_error(self, tmp_path: Path) -> None:
        """Rendering nonexistent template raises TemplateNotFound."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        renderer = Renderer(pages_dir, components_dir)

        with pytest.raises(TemplateNotFound):
            renderer.render(pages_dir / "nonexistent.html")

    def test_missing_component_raises_error(self, tmp_path: Path) -> None:
        """Rendering nonexistent component raises TemplateNotFound."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        renderer = Renderer(pages_dir, components_dir)

        with pytest.raises(TemplateNotFound):
            renderer.render_component(components_dir / "missing.html")

    def test_missing_include_raises_error(self, tmp_path: Path) -> None:
        """Including nonexistent template raises TemplateNotFound."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (pages_dir / "page.html").write_text("{% include 'missing.html' %}")

        renderer = Renderer(pages_dir, components_dir)

        with pytest.raises(TemplateNotFound):
            renderer.render(pages_dir / "page.html")


class TestFrameworkTemplates:
    """Tests for framework built-in templates."""

    def test_framework_base_template_available(self, tmp_path: Path) -> None:
        """Framework's zerojs/base.html is available."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        # Page extends zerojs/base.html (framework template)
        (pages_dir / "index.html").write_text(
            "{% extends 'zerojs/base.html' %}{% block content %}<h1>Hello</h1>{% endblock %}"
        )

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "index.html")

        assert "<!DOCTYPE html>" in result
        assert "<h1>Hello</h1>" in result
        assert 'src="https://unpkg.com/htmx.org@' in result
        assert 'integrity="sha384-' in result  # SRI enabled

    def test_user_base_template_separate_from_framework(self, tmp_path: Path) -> None:
        """User's base.html is separate from framework's zerojs/base.html."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        # User creates their own base.html
        (components_dir / "base.html").write_text("<html><body>USER{% block content %}{% endblock %}</body></html>")
        # Page extends user's base.html
        (pages_dir / "index.html").write_text("{% extends 'base.html' %}{% block content %}<p>Test</p>{% endblock %}")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "index.html")

        assert "USER" in result
        assert "<p>Test</p>" in result
        # Should NOT have framework's htmx include
        assert "htmx.org" not in result


class TestShadowComponents:
    """Tests for Shadow DOM components (.shadow.html)."""

    def test_shadow_component_wrapped_in_shadow_dom(self, tmp_path: Path) -> None:
        """Shadow components are wrapped in declarative Shadow DOM."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "card.shadow.html").write_text("<div class='card'>{{ title }}</div>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render_component(components_dir / "card.shadow.html", {"title": "Hello"})

        assert "<zjs-card>" in result
        assert '<template shadowrootmode="open">' in result
        assert "<div class='card'>Hello</div>" in result
        assert "</zjs-card>" in result

    def test_shadow_component_via_include(self, tmp_path: Path) -> None:
        """Shadow components work with {% include %}."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "badge.shadow.html").write_text(
            "<style>.badge { color: red; }</style><span class='badge'>{{ text }}</span>"
        )
        (pages_dir / "page.html").write_text("<main>{% include 'badge.shadow.html' %}</main>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render(pages_dir / "page.html", {"text": "New"})

        assert "<main>" in result
        assert "<zjs-badge>" in result
        assert '<template shadowrootmode="open">' in result
        assert "<span class='badge'>New</span>" in result

    def test_regular_component_not_wrapped(self, tmp_path: Path) -> None:
        """Regular .html components are NOT wrapped in Shadow DOM."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "header.html").write_text("<header>Logo</header>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render_component(components_dir / "header.html")

        assert result == "<header>Logo</header>"
        assert "<zjs-" not in result
        assert "shadowrootmode" not in result

    def test_shadow_component_name_from_filename(self, tmp_path: Path) -> None:
        """Shadow component tag name derived from filename."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (components_dir / "user_card.shadow.html").write_text("<div>Content</div>")

        renderer = Renderer(pages_dir, components_dir)
        result = renderer.render_component(components_dir / "user_card.shadow.html")

        # user_card -> zjs-user-card
        assert "<zjs-user-card>" in result
        assert "</zjs-user-card>" in result
