"""Shared fixtures for ZeroJS integration tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zerojs import ZeroJS


@pytest.fixture
def app_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure for testing."""
    # Create directories
    pages_dir = tmp_path / "pages"
    components_dir = tmp_path / "components"
    static_dir = tmp_path / "static"
    errors_dir = tmp_path / "errors"

    pages_dir.mkdir()
    components_dir.mkdir()
    static_dir.mkdir()
    errors_dir.mkdir()

    # Disable CSRF for tests
    (tmp_path / "settings.py").write_text("CSRF_ENABLED = False")

    # Create base template
    (components_dir / "base.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>{% block title %}Test{% endblock %}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>
""")

    # Create index page
    (pages_dir / "index.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Home</h1>{% endblock %}
""")

    # Create error pages
    (errors_dir / "404.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Not Found</h1>{% endblock %}
""")
    (errors_dir / "500.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Server Error</h1>{% endblock %}
""")

    return tmp_path


@pytest.fixture
def client(app_dir: Path) -> TestClient:
    """Create a test client for the ZeroJS app."""
    import os

    original_dir = os.getcwd()
    os.chdir(app_dir)

    # Disable CSRF for tests
    (app_dir / "settings.py").write_text("CSRF_ENABLED = False")

    try:
        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            static_dir=app_dir / "static",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        yield TestClient(app.asgi_app)
    finally:
        os.chdir(original_dir)
