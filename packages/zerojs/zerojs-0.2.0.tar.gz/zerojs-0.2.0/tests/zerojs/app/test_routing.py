"""Tests for routing functionality."""

from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestBasicRouting:
    """Tests for basic GET routing."""

    def test_index_route_returns_html(self, client: TestClient) -> None:
        """GET / returns 200 with HTML content."""
        response = client.get("/")

        assert response.status_code == 200
        assert "<h1>Home</h1>" in response.text

    def test_nonexistent_route_returns_404(self, client: TestClient) -> None:
        """GET /nonexistent returns 404 with custom error page."""
        response = client.get("/nonexistent")

        assert response.status_code == 404
        assert "<h1>Not Found</h1>" in response.text


class TestDynamicRoutes:
    """Tests for dynamic route parameters."""

    def test_dynamic_param_passed_to_template(self, app_dir: Path) -> None:
        """Dynamic route params are available in template."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>User {{ id }}</h1>{% endblock %}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/123")

        assert response.status_code == 200
        assert "<h1>User 123</h1>" in response.text


class TestStaticFiles:
    """Tests for static file serving."""

    def test_static_css_served(self, app_dir: Path) -> None:
        """Static CSS files are served correctly."""
        static_dir = app_dir / "static"
        css_dir = static_dir / "css"
        css_dir.mkdir(parents=True)

        (css_dir / "style.css").write_text("body { color: red; }")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            static_dir=static_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/static/css/style.css")

        assert response.status_code == 200
        assert "body { color: red; }" in response.text

    def test_static_js_served(self, app_dir: Path) -> None:
        """Static JavaScript files are served correctly."""
        static_dir = app_dir / "static"
        js_dir = static_dir / "js"
        js_dir.mkdir(parents=True)

        (js_dir / "app.js").write_text("console.log('hello');")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            static_dir=static_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/static/js/app.js")

        assert response.status_code == 200
        assert "console.log('hello');" in response.text

    def test_nonexistent_static_returns_404(self, app_dir: Path) -> None:
        """Request for nonexistent static file returns 404."""
        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            static_dir=app_dir / "static",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/static/nonexistent.css")

        assert response.status_code == 404


class TestStaticTextFiles:
    """Tests for static text file routing (.txt, .md)."""

    def test_txt_file_served_as_plain_text(self, app_dir: Path) -> None:
        """Text files in pages/ are served as plain text."""
        pages_dir = app_dir / "pages"

        (pages_dir / "robots.txt").write_text("User-agent: *\nDisallow: /admin")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/robots.txt")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "User-agent: *" in response.text
        assert "Disallow: /admin" in response.text

    def test_md_file_served_as_markdown(self, app_dir: Path) -> None:
        """Markdown files in pages/ are served with markdown content type."""
        pages_dir = app_dir / "pages"

        (pages_dir / "readme.md").write_text("# Hello World\n\nThis is markdown.")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/readme.md")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        assert "# Hello World" in response.text

    def test_nested_txt_file(self, app_dir: Path) -> None:
        """Nested text files maintain directory structure in URL."""
        pages_dir = app_dir / "pages"
        docs_dir = pages_dir / "docs"
        docs_dir.mkdir()

        (docs_dir / "license.txt").write_text("MIT License")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/docs/license.txt")

        assert response.status_code == 200
        assert "MIT License" in response.text
