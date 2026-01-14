"""Tests for Path type parameter validation against traversal attacks."""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestPathParamTraversalProtection:
    """Tests for Path parameter traversal protection."""

    def test_path_param_safe_value(self, app_dir: Path) -> None:
        """Safe path values work correctly."""
        pages_dir = app_dir / "pages"
        docs_dir = pages_dir / "docs"
        docs_dir.mkdir()

        (docs_dir / "[filename].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>File: {{ filename }}</p>{% endblock %}
""")

        (docs_dir / "_filename.py").write_text("""
from pathlib import Path

def get(filename: Path) -> dict:
    return {"filename": str(filename)}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/docs/readme.txt")
        assert response.status_code == 200
        assert "File: readme.txt" in response.text

    def test_path_param_dotfile_safe(self, app_dir: Path) -> None:
        """Dotfiles are safe (single dot prefix)."""
        pages_dir = app_dir / "pages"
        docs_dir = pages_dir / "docs"
        docs_dir.mkdir()

        (docs_dir / "[filename].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>File: {{ filename }}</p>{% endblock %}
""")

        (docs_dir / "_filename.py").write_text("""
from pathlib import Path

def get(filename: Path) -> dict:
    return {"filename": str(filename)}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/docs/.gitignore")
        assert response.status_code == 200
        assert "File: .gitignore" in response.text

    def test_path_param_traversal_blocked(self, app_dir: Path) -> None:
        """Path traversal attempts are blocked with 422."""
        pages_dir = app_dir / "pages"
        docs_dir = pages_dir / "docs"
        docs_dir.mkdir()

        (docs_dir / "[filename].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.filename }}</p>{% endif %}
<p>File page</p>
{% endblock %}
""")

        (docs_dir / "_filename.py").write_text("""
from pathlib import Path

def get(filename: Path) -> dict:
    return {"filename": str(filename)}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # Test parent traversal - URL-encoded ".." bypasses HTTP normalization
        # Raw "/docs/.." gets normalized to "/" by HTTP clients before routing
        # Attackers use encoding to bypass this normalization
        response = client.get("/docs/%2e%2e")  # %2e%2e = ".."
        assert response.status_code == 422

    def test_path_param_home_expansion_blocked(self, app_dir: Path) -> None:
        """Home directory expansion is blocked with 422."""
        pages_dir = app_dir / "pages"
        docs_dir = pages_dir / "docs"
        docs_dir.mkdir()

        (docs_dir / "[filename].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.filename }}</p>{% endif %}
<p>File page</p>
{% endblock %}
""")

        (docs_dir / "_filename.py").write_text("""
from pathlib import Path

def get(filename: Path) -> dict:
    return {"filename": str(filename)}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # Test home expansion
        response = client.get("/docs/~")
        assert response.status_code == 422

    def test_str_param_validated_by_default(self, app_dir: Path) -> None:
        """String params ARE validated for traversal (security by default)."""
        pages_dir = app_dir / "pages"
        search_dir = pages_dir / "search"
        search_dir.mkdir()

        (search_dir / "[query].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Query: {{ query }}</p>{% endblock %}
""")

        (search_dir / "_query.py").write_text("""
def get(query: str) -> dict:
    return {"query": query}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # String params are now validated by default
        response = client.get("/search/%2e%2e")  # %2e%2e = ".."
        assert response.status_code == 422

    def test_unsafe_str_param_opts_out(self, app_dir: Path) -> None:
        """UnsafeStr params opt out of traversal validation."""
        pages_dir = app_dir / "pages"
        search_dir = pages_dir / "search"
        search_dir.mkdir()

        (search_dir / "[query].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Query: {{ query }}</p>{% endblock %}
""")

        (search_dir / "_query.py").write_text("""
from zerojs import UnsafeStr

def get(query: UnsafeStr) -> dict:
    return {"query": query}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # UnsafeStr explicitly opts out of validation
        response = client.get("/search/%2e%2e")  # %2e%2e = ".."
        assert response.status_code == 200

    def test_path_param_in_post_handler(self, app_dir: Path) -> None:
        """Path traversal protection works in POST handlers too."""
        pages_dir = app_dir / "pages"
        files_dir = pages_dir / "files"
        files_dir.mkdir()

        (files_dir / "[filename].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.filename }}</p>{% endif %}
<p>File: {{ filename }}</p>
{% endblock %}
""")

        (files_dir / "_filename.py").write_text("""
from pathlib import Path

def get(filename: Path) -> dict:
    return {"filename": str(filename)}

def post(filename: Path) -> dict:
    return {"filename": str(filename), "uploaded": True}
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # Safe path works
        response = client.post("/files/document.pdf")
        assert response.status_code == 200

        # Traversal blocked - URL-encoded ".." to bypass HTTP normalization
        response = client.post("/files/%2e%2e")  # %2e%2e = ".."
        assert response.status_code == 422
