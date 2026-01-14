"""Tests for component POST handler (_register_component_post_handler)."""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestComponentPostHandler:
    """Tests for POST requests to components at /components/{name}."""

    def test_component_post_with_valid_pydantic_data(self, app_dir: Path) -> None:
        """POST to component with valid Pydantic data returns success."""
        components_dir = app_dir / "components"

        # Create component template
        (components_dir / "contact.html").write_text("""
<div id="contact">
{% if success %}<span class="success">Sent!</span>{% endif %}
<form method="POST"><input name="email"></form>
</div>
""")

        # Create component handler with Pydantic validation
        (components_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def post(data: ContactForm) -> dict:
    return {"success": True, "email": data.email}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/contact", data={"email": "test@example.com"})

        assert response.status_code == 200
        assert "Sent!" in response.text

    def test_component_post_with_invalid_pydantic_data(self, app_dir: Path) -> None:
        """POST to component with invalid Pydantic data returns 422."""
        components_dir = app_dir / "components"

        (components_dir / "contact.html").write_text("""
<div id="contact">
<form method="POST"><input name="email"></form>
</div>
""")

        (components_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def post(data: ContactForm) -> dict:
    return {"success": True}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/contact", data={"email": "invalid-email"})

        assert response.status_code == 422
        assert "email" in response.text.lower()

    def test_component_post_with_raw_dict_data(self, app_dir: Path) -> None:
        """POST to component with dict parameter receives raw form data."""
        components_dir = app_dir / "components"

        (components_dir / "feedback.html").write_text("""
<div id="feedback">
{% if message %}<span>{{ message }}</span>{% endif %}
<form method="POST"><input name="comment"></form>
</div>
""")

        (components_dir / "_feedback.py").write_text("""
def post(data: dict) -> dict:
    return {"message": f"Got: {data.get('comment')}"}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/feedback", data={"comment": "Hello!"})

        assert response.status_code == 200
        assert "Got: Hello!" in response.text

    def test_component_post_without_form_param(self, app_dir: Path) -> None:
        """POST to component handler without form param works."""
        components_dir = app_dir / "components"

        (components_dir / "counter.html").write_text("""
<div id="counter">
<span>Count: {{ count }}</span>
<button>Increment</button>
</div>
""")

        (components_dir / "_counter.py").write_text("""
count = 0

def post() -> dict:
    global count
    count += 1
    return {"count": count}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/counter")

        assert response.status_code == 200
        assert "Count: 1" in response.text

    def test_component_post_returns_response_directly(self, app_dir: Path) -> None:
        """POST handler returning Response object is returned directly."""
        components_dir = app_dir / "components"

        (components_dir / "redirect.html").write_text("""
<div id="redirect">Redirect component</div>
""")

        (components_dir / "_redirect.py").write_text("""
from fastapi.responses import RedirectResponse

def post() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app, follow_redirects=False)

        response = client.post("/components/redirect")

        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_component_post_with_query_params(self, app_dir: Path) -> None:
        """POST to component passes query params to handler."""
        components_dir = app_dir / "components"

        (components_dir / "item.html").write_text("""
<div id="item">
<span>Item {{ item_id }}: {{ status }}</span>
</div>
""")

        (components_dir / "_item.py").write_text("""
def post(item_id: str) -> dict:
    return {"item_id": item_id, "status": "updated"}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/item?item_id=123")

        assert response.status_code == 200
        assert "Item 123: updated" in response.text


class TestComponentPostCSRF:
    """Tests for CSRF protection in component POST handlers."""

    def test_component_post_csrf_validation_fails_without_token(self, app_dir: Path) -> None:
        """POST to component without CSRF token fails when CSRF enabled."""
        components_dir = app_dir / "components"

        (components_dir / "form.html").write_text("""
<div id="form">
{% if csrf_error %}<span class="error">CSRF failed</span>{% endif %}
<form method="POST"><input name="data"></form>
</div>
""")

        (components_dir / "_form.py").write_text("""
def post(data: dict) -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/form", data={"data": "test"})

        assert response.status_code == 200
        assert "CSRF failed" in response.text

    def test_component_post_csrf_validation_passes_with_valid_token(self, app_dir: Path) -> None:
        """POST to component with valid CSRF token succeeds."""
        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        # Create a page to get CSRF token from
        (pages_dir / "index.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Home</h1>{% endblock %}
""")

        (components_dir / "form.html").write_text("""
<div id="form">
{% if success %}<span class="ok">Success!</span>{% endif %}
<form method="POST"><input name="data"></form>
</div>
""")

        (components_dir / "_form.py").write_text("""
def post(data: dict) -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # GET the index page to get a CSRF token cookie
        get_response = client.get("/")
        csrf_token = get_response.cookies.get("csrf_token")

        # POST to component with the CSRF token
        response = client.post(
            "/components/form",
            data={"data": "test", "csrf_token": csrf_token},
        )

        assert response.status_code == 200
        assert "Success!" in response.text

    def test_component_post_csrf_exempt_route(self, app_dir: Path) -> None:
        """POST to CSRF exempt component route succeeds without token."""
        components_dir = app_dir / "components"

        (components_dir / "webhook.html").write_text("""
<div id="webhook">
{% if received %}<span>Received!</span>{% endif %}
</div>
""")

        (components_dir / "_webhook.py").write_text("""
def post(data: dict) -> dict:
    return {"received": True}
""")

        # Enable CSRF but exempt the component route
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = True
CSRF_EXEMPT_ROUTES = ["/components/webhook"]
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/components/webhook", data={"payload": "data"})

        assert response.status_code == 200
        assert "Received!" in response.text
