"""Tests for query parameter validation via type hints."""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestQueryParamIntConversion:
    """Tests for integer query parameter conversion."""

    def test_int_param_converted(self, app_dir: Path) -> None:
        """Query parameter with int type hint is converted to integer."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Page: {{ page }}, Type: {{ page_type }}</p>{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(page: int = 1) -> dict:
    return {"page": page, "page_type": type(page).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/items?page=5")
        assert response.status_code == 200
        assert "Page: 5" in response.text
        assert "Type: int" in response.text

    def test_invalid_int_returns_422(self, app_dir: Path) -> None:
        """Invalid integer query parameter returns 422."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.page }}</p>{% endif %}
<p>Items page</p>
{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(page: int = 1) -> dict:
    return {"page": page}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/items?page=abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text


class TestQueryParamDefaultValue:
    """Tests for query parameters with default values."""

    def test_default_value_used_when_missing(self, app_dir: Path) -> None:
        """Query param with default is used when not provided."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Page: {{ page }}, Limit: {{ limit }}</p>{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(page: int = 1, limit: int = 10) -> dict:
    return {"page": page, "limit": limit}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # No query params - use defaults
        response = client.get("/items")
        assert response.status_code == 200
        assert "Page: 1" in response.text
        assert "Limit: 10" in response.text

        # Partial query params
        response = client.get("/items?page=3")
        assert response.status_code == 200
        assert "Page: 3" in response.text
        assert "Limit: 10" in response.text


class TestQueryParamRequired:
    """Tests for required query parameters (no default)."""

    def test_missing_required_returns_422(self, app_dir: Path) -> None:
        """Missing required query parameter returns 422."""
        pages_dir = app_dir / "pages"

        (pages_dir / "search.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.query }}</p>{% endif %}
<p>Search results</p>
{% endblock %}
""")

        (pages_dir / "_search.py").write_text("""
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

        response = client.get("/search")
        assert response.status_code == 422
        assert "Missing required query parameter" in response.text

    def test_provided_required_works(self, app_dir: Path) -> None:
        """Provided required query parameter works correctly."""
        pages_dir = app_dir / "pages"

        (pages_dir / "search.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Query: {{ query }}</p>{% endblock %}
""")

        (pages_dir / "_search.py").write_text("""
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

        response = client.get("/search?query=hello")
        assert response.status_code == 200
        assert "Query: hello" in response.text


class TestQueryParamBoolConversion:
    """Tests for boolean query parameter conversion."""

    def test_bool_param_true_values(self, app_dir: Path) -> None:
        """Query parameter with bool type hint converts 'true', '1', 'yes' to True."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Active: {{ active }}, Type: {{ active_type }}</p>{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(active: bool = False) -> dict:
    return {"active": active, "active_type": type(active).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        for value in ["true", "1", "yes", "True", "YES"]:
            response = client.get(f"/items?active={value}")
            assert response.status_code == 200
            assert "Active: True" in response.text
            assert "Type: bool" in response.text

    def test_bool_param_false_values(self, app_dir: Path) -> None:
        """Query parameter with bool type hint converts other values to False."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Active: {{ active }}</p>{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(active: bool = True) -> dict:
    return {"active": active}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        for value in ["false", "0", "no", "anything"]:
            response = client.get(f"/items?active={value}")
            assert response.status_code == 200
            assert "Active: False" in response.text


class TestQueryParamWithPathParam:
    """Tests for query parameters alongside path parameters."""

    def test_query_and_path_params_work_together(self, app_dir: Path) -> None:
        """Query params work correctly with path params."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}
<p>User ID: {{ user_id }}, Page: {{ page }}, Limit: {{ limit }}</p>
{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int, page: int = 1, limit: int = 10) -> dict:
    return {"user_id": id, "page": page, "limit": limit}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/123?page=2&limit=20")
        assert response.status_code == 200
        assert "User ID: 123" in response.text
        assert "Page: 2" in response.text
        assert "Limit: 20" in response.text

    def test_invalid_query_with_valid_path(self, app_dir: Path) -> None:
        """Invalid query param returns 422 even with valid path param."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.page }}</p>{% endif %}
<p>User page</p>
{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
def get(id: int, page: int = 1) -> dict:
    return {"user_id": id, "page": page}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/123?page=abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text


class TestQueryParamPostHandler:
    """Tests for query parameter validation in POST handlers."""

    def test_post_handler_validates_query_params(self, app_dir: Path) -> None:
        """POST handler validates query parameters."""
        pages_dir = app_dir / "pages"

        (pages_dir / "items.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<p class="error">{{ errors.page }}</p>{% endif %}
<p>Items page: {{ page }}</p>
{% endblock %}
""")

        (pages_dir / "_items.py").write_text("""
def get(page: int = 1) -> dict:
    return {"page": page}

def post(page: int = 1) -> dict:
    return {"page": page, "posted": True}
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

        # Valid query param
        response = client.post("/items?page=5")
        assert response.status_code == 200

        # Invalid query param
        response = client.post("/items?page=abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text


class TestQueryParamFloatConversion:
    """Tests for float query parameter conversion."""

    def test_float_param_converted(self, app_dir: Path) -> None:
        """Query parameter with float type hint is converted to float."""
        pages_dir = app_dir / "pages"

        (pages_dir / "prices.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Min: {{ min_price }}, Type: {{ price_type }}</p>{% endblock %}
""")

        (pages_dir / "_prices.py").write_text("""
def get(min_price: float = 0.0) -> dict:
    return {"min_price": min_price, "price_type": type(min_price).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/prices?min_price=19.99")
        assert response.status_code == 200
        assert "Min: 19.99" in response.text
        assert "Type: float" in response.text


class TestComponentQueryParamValidation:
    """Tests for query parameter validation in component handlers."""

    def test_component_validates_query_params(self, app_dir: Path) -> None:
        """Component handler validates query parameters."""
        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        (pages_dir / "index.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>Home</p>{% endblock %}
""")

        (components_dir / "counter.html").write_text("""
{% if errors %}
<p class="error">{{ errors.count }}</p>
{% else %}
<p>Count: {{ count }}, Type: {{ count_type }}</p>
{% endif %}
""")

        (components_dir / "_counter.py").write_text("""
def get(count: int = 0) -> dict:
    return {"count": count, "count_type": type(count).__name__}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # Valid query param
        response = client.get("/components/counter?count=5")
        assert response.status_code == 200
        assert "Count: 5" in response.text
        assert "Type: int" in response.text

        # Invalid query param
        response = client.get("/components/counter?count=abc")
        assert response.status_code == 422
        assert "Invalid value" in response.text
