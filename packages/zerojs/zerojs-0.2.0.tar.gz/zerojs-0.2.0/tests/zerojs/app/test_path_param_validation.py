"""Tests for path parameter validation via type hints."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestPathParamIntConversion:
    """Tests for integer path parameter conversion."""

    def test_int_param_converted(self, app_dir: Path) -> None:
        """Path parameter with int type hint is converted to integer."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>ID: {{ id }}, Type: {{ id_type }}</p>{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int) -> dict:
    return {"id": id, "id_type": type(id).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/123")
        assert response.status_code == 200
        assert "ID: 123" in response.text
        assert "Type: int" in response.text

    def test_invalid_int_returns_422(self, app_dir: Path) -> None:
        """Invalid integer path parameter returns 422."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.id }}</p>{% endif %}
<p>User page</p>
{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int) -> dict:
    return {"id": id}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text


class TestPathParamTypeHintRequired:
    """Tests for required type hints on path parameters."""

    def test_missing_type_hint_raises_error(self, app_dir: Path) -> None:
        """Missing type hint on path parameter raises TypeError at startup."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>User {{ id }}</p>{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id) -> dict:
    return {"id": id}
""")

        os.chdir(app_dir)

        with pytest.raises(TypeError, match="missing type hints for path parameters: id"):
            ZeroJS(
                pages_dir=pages_dir,
                components_dir=app_dir / "components",
                errors_dir=app_dir / "errors",
            )

    def test_str_type_hint_works(self, app_dir: Path) -> None:
        """Path parameter with str type hint works correctly."""
        pages_dir = app_dir / "pages"
        items_dir = pages_dir / "items"
        items_dir.mkdir()

        (items_dir / "[slug].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Slug: {{ slug }}, Type: {{ slug_type }}</p>{% endblock %}
""")

        (items_dir / "_slug.py").write_text("""
def get(slug: str) -> dict:
    return {"slug": slug, "slug_type": type(slug).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/items/my-item-slug")
        assert response.status_code == 200
        assert "Slug: my-item-slug" in response.text
        assert "Type: str" in response.text


class TestPathParamFloatConversion:
    """Tests for float path parameter conversion."""

    def test_float_param_converted(self, app_dir: Path) -> None:
        """Path parameter with float type hint is converted to float."""
        pages_dir = app_dir / "pages"
        prices_dir = pages_dir / "prices"
        prices_dir.mkdir()

        (prices_dir / "[amount].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Amount: {{ amount }}, Type: {{ amount_type }}</p>{% endblock %}
""")

        (prices_dir / "_amount.py").write_text("""
def get(amount: float) -> dict:
    return {"amount": amount, "amount_type": type(amount).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/prices/19.99")
        assert response.status_code == 200
        assert "Amount: 19.99" in response.text
        assert "Type: float" in response.text


class TestPathParamBoolConversion:
    """Tests for boolean path parameter conversion."""

    def test_bool_param_true_values(self, app_dir: Path) -> None:
        """Path parameter with bool type hint converts 'true', '1', 'yes' to True."""
        pages_dir = app_dir / "pages"
        flags_dir = pages_dir / "flags"
        flags_dir.mkdir()

        (flags_dir / "[enabled].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Enabled: {{ enabled }}, Type: {{ enabled_type }}</p>{% endblock %}
""")

        (flags_dir / "_enabled.py").write_text("""
def get(enabled: bool) -> dict:
    return {"enabled": enabled, "enabled_type": type(enabled).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        for value in ["true", "1", "yes", "True", "YES"]:
            response = client.get(f"/flags/{value}")
            assert response.status_code == 200
            assert "Enabled: True" in response.text
            assert "Type: bool" in response.text

    def test_bool_param_false_values(self, app_dir: Path) -> None:
        """Path parameter with bool type hint converts other values to False."""
        pages_dir = app_dir / "pages"
        flags_dir = pages_dir / "flags"
        flags_dir.mkdir()

        (flags_dir / "[enabled].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Enabled: {{ enabled }}</p>{% endblock %}
""")

        (flags_dir / "_enabled.py").write_text("""
def get(enabled: bool) -> dict:
    return {"enabled": enabled}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        for value in ["false", "0", "no", "anything"]:
            response = client.get(f"/flags/{value}")
            assert response.status_code == 200
            assert "Enabled: False" in response.text


class TestPathParamUUIDConversion:
    """Tests for UUID path parameter conversion."""

    def test_uuid_param_converted(self, app_dir: Path) -> None:
        """Path parameter with UUID type hint is converted to UUID."""
        pages_dir = app_dir / "pages"
        resources_dir = pages_dir / "resources"
        resources_dir.mkdir()

        (resources_dir / "[uuid].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>UUID: {{ resource_uuid }}, Type: {{ uuid_type }}</p>{% endblock %}
""")

        (resources_dir / "_uuid.py").write_text("""
import uuid

def get(uuid: uuid.UUID) -> dict:
    return {"resource_uuid": str(uuid), "uuid_type": type(uuid).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/resources/{test_uuid}")
        assert response.status_code == 200
        assert f"UUID: {test_uuid}" in response.text
        assert "Type: UUID" in response.text

    def test_invalid_uuid_returns_422(self, app_dir: Path) -> None:
        """Invalid UUID path parameter returns 422."""
        pages_dir = app_dir / "pages"
        resources_dir = pages_dir / "resources"
        resources_dir.mkdir()

        (resources_dir / "[uuid].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.uuid }}</p>{% endif %}
<p>Resource page</p>
{% endblock %}
""")

        (resources_dir / "_uuid.py").write_text("""
import uuid

def get(uuid: uuid.UUID) -> dict:
    return {"uuid": uuid}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/resources/not-a-uuid")
        assert response.status_code == 422
        assert "Invalid value" in response.text


class TestPathParamPostHandler:
    """Tests for path parameter validation in POST handlers."""

    def test_post_handler_validates_int_param(self, app_dir: Path) -> None:
        """POST handler validates integer path parameters."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.id }}</p>{% endif %}
<p>User ID: {{ id }}</p>
{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int) -> dict:
    return {"id": id}

def post(id: int) -> dict:
    return {"id": id, "updated": True}
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

        # Valid int
        response = client.post("/users/123")
        assert response.status_code == 200

        # Invalid int
        response = client.post("/users/abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text

    def test_post_handler_missing_type_hint_raises_error(self, app_dir: Path) -> None:
        """POST handler missing type hint raises TypeError at startup."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>User {{ id }}</p>{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int) -> dict:
    return {"id": id}

def post(id) -> dict:
    return {"id": id}
""")

        os.chdir(app_dir)

        with pytest.raises(TypeError, match="missing type hints for path parameters: id"):
            ZeroJS(
                pages_dir=pages_dir,
                components_dir=app_dir / "components",
                errors_dir=app_dir / "errors",
            )
