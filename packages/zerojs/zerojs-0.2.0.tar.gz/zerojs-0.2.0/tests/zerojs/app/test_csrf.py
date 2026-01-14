"""Tests for CSRF protection."""

from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestCSRFProtection:
    """Tests for CSRF protection."""

    def test_get_sets_csrf_cookie(self, app_dir: Path) -> None:
        """GET request sets CSRF token cookie."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable CSRF for this test
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/")

        assert response.status_code == 200
        assert "csrf_token" in response.cookies
        # Token should be 64 hex chars (32 bytes)
        assert len(response.cookies["csrf_token"]) == 64

    def test_post_with_valid_csrf_succeeds(self, app_dir: Path) -> None:
        """POST with matching cookie and form tokens succeeds."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Create form page and handler
        (pages_dir / "contact.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if success %}<div class="success">Sent!</div>{% endif %}
<form method="POST">
    {{ csrf_input(csrf_token) }}
    <input name="message">
</form>
{% endblock %}
""")

        (pages_dir / "_contact.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First GET to get the token
        get_response = client.get("/contact")
        csrf_token = get_response.cookies["csrf_token"]

        # Set cookie on client instance (not per-request)
        client.cookies.set("csrf_token", csrf_token)

        # POST with matching token
        response = client.post(
            "/contact",
            data={"csrf_token": csrf_token, "message": "Hello"},
        )

        assert response.status_code == 200
        assert "Sent!" in response.text

    def test_post_without_csrf_returns_403(self, app_dir: Path) -> None:
        """POST without CSRF token returns 403 and re-renders form with error."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if csrf_error %}<div class="error">Session expired</div>{% endif %}
<form method="POST"></form>
{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # POST without any CSRF token
        response = client.post("/action", data={})

        assert response.status_code == 403
        assert "Session expired" in response.text

    def test_post_with_mismatched_csrf_returns_403(self, app_dir: Path) -> None:
        """POST with mismatched tokens returns 403 and re-renders form with error."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if csrf_error %}<div class="error">Session expired</div>{% endif %}
<form method="POST"></form>
{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        # Enable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # GET to get a valid token
        get_response = client.get("/action")
        cookie_token = get_response.cookies["csrf_token"]

        # Set cookie on client instance (not per-request)
        client.cookies.set("csrf_token", cookie_token)

        # POST with different form token
        response = client.post(
            "/action",
            data={"csrf_token": "wrong_token_value"},
        )

        assert response.status_code == 403
        assert "Session expired" in response.text

    def test_csrf_exempt_route_bypasses_validation(self, app_dir: Path) -> None:
        """Routes in CSRF_EXEMPT_ROUTES skip CSRF validation."""
        pages_dir = app_dir / "pages"
        api_dir = pages_dir / "api"
        api_dir.mkdir()
        import os

        os.chdir(app_dir)

        (api_dir / "webhook.html").write_text("""
{% extends 'base.html' %}
{% block content %}<div>Webhook endpoint</div>{% endblock %}
""")

        (api_dir / "_webhook.py").write_text("""
def post() -> dict:
    return {"received": True}
""")

        # Enable CSRF with exempt route
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = True
CSRF_EXEMPT_ROUTES = ["/api/webhook"]
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # POST without CSRF token should succeed for exempt route
        response = client.post("/api/webhook", data={})

        assert response.status_code == 200

    def test_csrf_disabled_allows_post_without_token(self, app_dir: Path) -> None:
        """When CSRF_ENABLED=False, POST works without token."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if success %}<div>OK</div>{% endif %}
{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        # Explicitly disable CSRF
        (app_dir / "settings.py").write_text("CSRF_ENABLED = False")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.post("/action", data={})

        assert response.status_code == 200
        assert "OK" in response.text

    def test_custom_csrf_token_name(self, app_dir: Path) -> None:
        """Custom CSRF_TOKEN_NAME setting is respected."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "form.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if success %}<div>Done</div>{% endif %}
<form method="POST">
    <input type="hidden" name="_token" value="{{ csrf_token }}">
</form>
{% endblock %}
""")

        (pages_dir / "_form.py").write_text("""
def post() -> dict:
    return {"success": True}
""")

        # Enable CSRF with custom token name
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = True
CSRF_TOKEN_NAME = "_token"
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # GET to get token (with custom cookie name)
        get_response = client.get("/form")
        csrf_token = get_response.cookies["_token"]

        # Set cookie on client instance (not per-request)
        client.cookies.set("_token", csrf_token)

        # POST with custom field name
        response = client.post(
            "/form",
            data={"_token": csrf_token},
        )

        assert response.status_code == 200
        assert "Done" in response.text

    def test_csrf_cookie_secure_false_by_default(self, app_dir: Path) -> None:
        """CSRF cookie does not have Secure flag by default."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (app_dir / "settings.py").write_text("CSRF_ENABLED = True")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/")

        assert response.status_code == 200
        # Check Set-Cookie header does not contain Secure flag
        set_cookie = response.headers.get("set-cookie", "")
        assert "csrf_token=" in set_cookie
        assert "; secure" not in set_cookie.lower()

    def test_csrf_cookie_secure_true(self, app_dir: Path) -> None:
        """CSRF cookie has Secure flag when CSRF_COOKIE_SECURE=True."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = True
CSRF_COOKIE_SECURE = True
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/")

        assert response.status_code == 200
        # Check Set-Cookie header contains Secure flag
        set_cookie = response.headers.get("set-cookie", "")
        assert "csrf_token=" in set_cookie
        assert "; secure" in set_cookie.lower()
