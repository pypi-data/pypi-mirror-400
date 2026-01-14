"""Tests for handler return types and redirects."""

from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestRedirects:
    """Tests for redirect handling."""

    def test_redirect_string_returns_303(self, app_dir: Path) -> None:
        """Handler returning '/path' redirects with 303."""
        pages_dir = app_dir / "pages"

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}<form method="POST"></form>{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
def post() -> str:
    return "/success"
""")

        (pages_dir / "success.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Success!</h1>{% endblock %}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app, follow_redirects=False)

        response = client.post("/action")

        assert response.status_code == 303
        assert response.headers["location"] == "/success"

    def test_htmx_redirect_uses_header(self, app_dir: Path) -> None:
        """HTMX request redirect uses HX-Redirect header."""
        pages_dir = app_dir / "pages"

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}<form method="POST"></form>{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
def post() -> str:
    return "/success"
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post(
            "/action",
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        assert response.headers.get("HX-Redirect") == "/success"


class TestHandlerReturnTypes:
    """Tests for different handler return types."""

    def test_dict_return_renders_template(self, app_dir: Path) -> None:
        """Handler returning dict renders template with context."""
        pages_dir = app_dir / "pages"

        (pages_dir / "data.html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>{{ message }}</p>{% endblock %}
""")

        (pages_dir / "_data.py").write_text("""
def get() -> dict:
    return {"message": "Hello from handler!"}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/data")

        assert response.status_code == 200
        assert "Hello from handler!" in response.text

    def test_get_handler_receives_path_params(self, app_dir: Path) -> None:
        """GET handler receives URL path parameters."""
        pages_dir = app_dir / "pages"
        users_dir = pages_dir / "users"
        users_dir.mkdir()

        (users_dir / "[id].html").write_text("""
{% extends 'base.html' %}
{% block content %}<p>{{ user_name }}</p>{% endblock %}
""")

        (users_dir / "_id.py").write_text("""
USERS = {"1": "Alice", "2": "Bob"}

def get(id: str) -> dict:
    return {"user_name": USERS.get(id, "Unknown")}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/users/1")
        assert "Alice" in response.text

        response = client.get("/users/2")
        assert "Bob" in response.text


class TestCSRFErrorWithGetContext:
    """Tests for CSRF error handling with GET handler context (line 808)."""

    def test_csrf_error_merges_get_handler_context(self, app_dir: Path) -> None:
        """CSRF error includes context from GET handler."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "form.html").write_text("""
{% extends 'base.html' %}
{% block content %}
<h1>{{ page_title }}</h1>
{% if csrf_error %}<span class="error">CSRF failed</span>{% endif %}
<form method="POST"><input name="data"></form>
{% endblock %}
""")

        (pages_dir / "_form.py").write_text("""
def get() -> dict:
    return {"page_title": "Contact Form"}

def post(data: dict) -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # POST without CSRF token should fail but include GET handler context
        response = client.post("/form", data={"data": "test"})

        assert response.status_code == 403
        assert "CSRF failed" in response.text
        assert "Contact Form" in response.text  # GET handler context merged


class TestCSRFErrorHtmxComponent:
    """Tests for CSRF error with HTMX component rendering (line 820)."""

    def test_csrf_error_htmx_renders_component(self, app_dir: Path) -> None:
        """CSRF error with HTMX request renders target component."""
        import os

        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        (pages_dir / "page.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% include 'components/contact_form.html' %}
{% endblock %}
""")

        (pages_dir / "_page.py").write_text("""
def post(data: dict) -> dict:
    return {"success": True}
""")

        (components_dir / "contact_form.html").write_text("""
<div id="contact-form">
{% if csrf_error %}<span class="error">CSRF error in component</span>{% endif %}
<form method="POST" hx-post="/page" hx-target="#contact-form">
<input name="email">
</form>
</div>
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

        # HTMX POST without CSRF token
        response = client.post(
            "/page",
            data={"email": "test@example.com"},
            headers={"HX-Request": "true", "HX-Target": "#contact-form"},
        )

        # Should return 200 for HTMX with just the component
        assert response.status_code == 200
        assert "CSRF error in component" in response.text
        # Should NOT contain the full page (no base.html)
        assert "<!DOCTYPE html>" not in response.text


class TestValidationErrorWithGetContext:
    """Tests for validation error handling with GET handler context (line 852)."""

    def test_validation_error_merges_get_handler_context(self, app_dir: Path) -> None:
        """Validation error includes context from GET handler."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "contact.html").write_text("""
{% extends 'base.html' %}
{% block content %}
<h1>{{ page_title }}</h1>
{% if errors %}<span class="error">{{ errors.email }}</span>{% endif %}
<form method="POST"><input name="email"></form>
{% endblock %}
""")

        (pages_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def get() -> dict:
    return {"page_title": "Contact Us"}

def post(data: ContactForm) -> dict:
    return {"success": True}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        # POST with invalid email
        response = client.post("/contact", data={"email": "not-an-email"})

        assert response.status_code == 422
        assert "Contact Us" in response.text  # GET handler context merged
        assert "email" in response.text.lower()  # Validation error shown


class TestDictFormParam:
    """Tests for handler with dict form parameter (line 875)."""

    def test_handler_receives_raw_dict_form_data(self, app_dir: Path) -> None:
        """POST handler with dict param receives raw form data."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "feedback.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if result %}<span>Got: {{ result }}</span>{% endif %}
<form method="POST">
<input name="name">
<input name="message">
</form>
{% endblock %}
""")

        (pages_dir / "_feedback.py").write_text("""
def post(data: dict) -> dict:
    return {"result": f"{data.get('name')}: {data.get('message')}"}
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/feedback", data={"name": "John", "message": "Hello!"})

        assert response.status_code == 200
        assert "John: Hello!" in response.text


class TestRateLimitWithFormData:
    """Tests for rate limit error with form data preservation (line 886)."""

    def test_rate_limit_preserves_form_data(self, app_dir: Path) -> None:
        """Rate limit error preserves submitted form data in values."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "submit.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if rate_limit_error %}<span class="error">Too many requests</span>{% endif %}
{% if success %}<span class="success">Done!</span>{% endif %}
<form method="POST">
<input name="email" value="{{ values.email if values else '' }}">
</form>
{% endblock %}
""")

        (pages_dir / "_submit.py").write_text("""
from zerojs import rate_limit

@rate_limit("1/minute")
def post(data: dict) -> dict:
    return {"success": True}
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First request should succeed
        response1 = client.post("/submit", data={"email": "test@example.com"})
        assert response1.status_code == 200
        assert "Done!" in response1.text

        # Second request should be rate limited but preserve form data
        response2 = client.post("/submit", data={"email": "preserved@example.com"})
        assert response2.status_code == 429
        assert "Too many requests" in response2.text
        assert "preserved@example.com" in response2.text  # Form data preserved


class TestRateLimitHtmxComponent:
    """Tests for rate limit error with HTMX component rendering (line 912)."""

    def test_rate_limit_htmx_renders_component(self, app_dir: Path) -> None:
        """Rate limit error with HTMX request renders target component."""
        import os

        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        (pages_dir / "page.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% include 'components/submit_form.html' %}
{% endblock %}
""")

        (pages_dir / "_page.py").write_text("""
from zerojs import rate_limit

@rate_limit("1/minute")
def post(data: dict) -> dict:
    return {"success": True}
""")

        (components_dir / "submit_form.html").write_text("""
<div id="submit-form">
{% if success %}<span class="success">Success!</span>{% endif %}
{% if rate_limit_error %}<span class="error">Rate limited in component</span>{% endif %}
<form method="POST" hx-post="/page" hx-target="#submit-form">
<input name="data">
</form>
</div>
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First HTMX request should succeed
        response1 = client.post(
            "/page",
            data={"data": "test"},
            headers={"HX-Request": "true", "HX-Target": "#submit-form"},
        )
        assert response1.status_code == 200
        assert "Success!" in response1.text

        # Second HTMX request should be rate limited
        response = client.post(
            "/page",
            data={"data": "test"},
            headers={"HX-Request": "true", "HX-Target": "#submit-form"},
        )

        # Should return 200 for HTMX with just the component
        assert response.status_code == 200
        assert "Rate limited in component" in response.text
        # Should NOT contain the full page
        assert "<!DOCTYPE html>" not in response.text


class TestHandlerReturnsResponse:
    """Tests for handler returning Response directly (line 923)."""

    def test_handler_returns_response_directly(self, app_dir: Path) -> None:
        """Handler returning Response object passes through directly."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "custom.html").write_text("""
{% extends 'base.html' %}
{% block content %}<form method="POST"></form>{% endblock %}
""")

        (pages_dir / "_custom.py").write_text("""
from fastapi.responses import JSONResponse

def post() -> JSONResponse:
    return JSONResponse(content={"status": "ok"}, status_code=201)
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/custom")

        assert response.status_code == 201
        assert response.json() == {"status": "ok"}


class TestHandlerReturnsNonRedirectString:
    """Tests for handler returning non-redirect string (line 936)."""

    def test_handler_returns_html_string(self, app_dir: Path) -> None:
        """Handler returning string not starting with / returns as HTML."""
        import os

        pages_dir = app_dir / "pages"

        (pages_dir / "html.html").write_text("""
{% extends 'base.html' %}
{% block content %}<form method="POST"></form>{% endblock %}
""")

        (pages_dir / "_html.py").write_text("""
def post() -> str:
    return "<div class='custom'>Custom HTML response</div>"
""")

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/html")

        assert response.status_code == 200
        assert "<div class='custom'>Custom HTML response</div>" in response.text
