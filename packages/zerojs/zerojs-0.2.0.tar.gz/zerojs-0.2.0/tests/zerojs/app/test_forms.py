"""Tests for form handling and validation."""

from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestFormValidation:
    """Tests for form handling and Pydantic validation."""

    def test_post_with_valid_data_returns_success(self, app_dir: Path) -> None:
        """POST with valid Pydantic data calls handler and returns success."""
        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        # Create form page
        (pages_dir / "contact.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if success %}<div class="success">Message sent!</div>{% endif %}
<form method="POST"><input name="email"></form>
{% endblock %}
""")

        # Create handler
        (pages_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def post(data: ContactForm) -> dict:
    return {"success": True}
""")

        # Create form component for HTMX
        (components_dir / "contact.html").write_text("""
{% if success %}<div class="success">Message sent!</div>{% endif %}
<form id="contact" method="POST"><input name="email"></form>
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/contact", data={"email": "test@example.com"})

        assert response.status_code == 200
        assert "Message sent!" in response.text

    def test_post_with_invalid_data_returns_errors(self, app_dir: Path) -> None:
        """POST with invalid data returns errors dict in context."""
        pages_dir = app_dir / "pages"

        # Create form page with error display
        (pages_dir / "contact.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if errors %}<div class="error">{{ errors.email }}</div>{% endif %}
<form method="POST"><input name="email" value="{{ values.email if values else '' }}"></form>
{% endblock %}
""")

        # Create handler with validation
        (pages_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def post(data: ContactForm) -> dict:
    return {"success": True}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/contact", data={"email": "invalid-email"})

        assert response.status_code == 422
        assert "error" in response.text.lower()

    def test_validation_errors_preserve_values(self, app_dir: Path) -> None:
        """Invalid form preserves submitted values for re-display."""
        pages_dir = app_dir / "pages"

        (pages_dir / "signup.html").write_text("""
{% extends 'base.html' %}
{% block content %}
<input name="name" value="{{ values.name if values else '' }}">
<input name="email" value="{{ values.email if values else '' }}">
{% endblock %}
""")

        (pages_dir / "_signup.py").write_text("""
from pydantic import BaseModel, EmailStr

class SignupForm(BaseModel):
    name: str
    email: EmailStr

def post(data: SignupForm) -> dict:
    return {"success": True}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/signup", data={"name": "John", "email": "bad"})

        assert response.status_code == 422
        assert 'value="John"' in response.text


class TestHTMXIntegration:
    """Tests for HTMX partial rendering."""

    def test_htmx_post_renders_component_only(self, app_dir: Path) -> None:
        """HTMX POST with HX-Target renders only the component."""
        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        # Full page template
        (pages_dir / "form.html").write_text("""
{% extends 'base.html' %}
{% block content %}
<h1>Page Title</h1>
{% include 'my_form.html' %}
{% endblock %}
""")

        # Component template
        (components_dir / "my_form.html").write_text("""
<form id="my-form">
{% if success %}<div class="success">Done!</div>{% endif %}
<button>Submit</button>
</form>
""")

        # Handler
        (pages_dir / "_form.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post(
            "/form",
            headers={"HX-Request": "true", "HX-Target": "#my-form"},
        )

        assert response.status_code == 200
        assert "Done!" in response.text
        # Should NOT contain full page elements
        assert "<h1>Page Title</h1>" not in response.text
        assert "<!DOCTYPE" not in response.text

    def test_htmx_validation_error_renders_component(self, app_dir: Path) -> None:
        """HTMX POST with validation error renders component with errors."""
        pages_dir = app_dir / "pages"
        components_dir = app_dir / "components"

        (pages_dir / "contact.html").write_text("""
{% extends 'base.html' %}
{% block content %}
<h1>Contact Us</h1>
{% include 'contact_form.html' %}
{% endblock %}
""")

        (components_dir / "contact_form.html").write_text("""
<form id="contact-form">
{% if errors %}<span class="error">{{ errors.email }}</span>{% endif %}
<input name="email" value="{{ values.email if values else '' }}">
</form>
""")

        (pages_dir / "_contact.py").write_text("""
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr

def post(data: ContactForm) -> dict:
    return {"success": True}
""")

        import os

        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            errors_dir=app_dir / "errors",
        )
        client = TestClient(app.asgi_app)

        response = client.post(
            "/contact",
            data={"email": "invalid"},
            headers={"HX-Request": "true", "HX-Target": "#contact-form"},
        )

        # HTMX requests get 200 for validation errors (so content swaps)
        assert response.status_code == 200
        assert "error" in response.text.lower()
        assert "<h1>Contact Us</h1>" not in response.text
