"""Tests for custom error pages."""

from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestErrorPages:
    """Tests for custom error pages."""

    def test_500_error_page_on_handler_exception(self, app_dir: Path) -> None:
        """Handler exception returns 500 with custom error page."""
        pages_dir = app_dir / "pages"

        (pages_dir / "broken.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>This page</h1>{% endblock %}
""")

        (pages_dir / "_broken.py").write_text("""
def get() -> dict:
    raise ValueError("Something went wrong!")
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app, raise_server_exceptions=False)

        response = client.get("/broken")

        assert response.status_code == 500
        assert "<h1>Server Error</h1>" in response.text
