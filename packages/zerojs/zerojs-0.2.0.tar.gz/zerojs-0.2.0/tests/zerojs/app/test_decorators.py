"""Tests for ZeroJS decorators."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import time_machine
from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestRateLimitDecorator:
    """Tests for @rate_limit decorator."""

    def test_rate_limit_decorator_on_get_handler(self, app_dir: Path) -> None:
        """@rate_limit decorator applies per-route rate limiting on GET."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "limited.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Limited</h1>{% endblock %}
""")

        # Handler with rate_limit decorator - stricter than global default
        (pages_dir / "_limited.py").write_text("""
from zerojs import rate_limit

@rate_limit("1/minute")
def get() -> dict:
    return {}
""")

        # Enable rate limiting middleware with permissive global default
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First request should succeed
        response1 = client.get("/limited")
        assert response1.status_code == 200

        # Second request should be rate limited (1/minute limit)
        response2 = client.get("/limited")
        assert response2.status_code == 429

    def test_rate_limit_decorator_on_post_handler(self, app_dir: Path) -> None:
        """@rate_limit decorator works on POST handlers."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "action.html").write_text("""
{% extends 'base.html' %}
{% block content %}{% if success %}OK{% endif %}{% endblock %}
""")

        (pages_dir / "_action.py").write_text("""
from zerojs import rate_limit

def get() -> dict:
    return {}

@rate_limit("1/minute")
def post() -> dict:
    return {"success": True}
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First POST should succeed
        response1 = client.post("/action", data={})
        assert response1.status_code == 200

        # Second POST should be rate limited
        response2 = client.post("/action", data={})
        assert response2.status_code == 429

        # GET should still work (different handler, no rate limit)
        response3 = client.get("/action")
        assert response3.status_code == 200

    def test_rate_limit_decorator_without_middleware(self, app_dir: Path) -> None:
        """@rate_limit decorator is ignored if RateLimitMiddleware not enabled."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "limited.html").write_text("""
{% extends 'base.html' %}
{% block content %}<h1>Limited</h1>{% endblock %}
""")

        (pages_dir / "_limited.py").write_text("""
from zerojs import rate_limit

@rate_limit("1/minute")
def get() -> dict:
    return {}
""")

        # No rate limiting middleware
        (app_dir / "settings.py").write_text("CSRF_ENABLED = False")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # Both requests should succeed (no middleware = no rate limiting)
        response1 = client.get("/limited")
        assert response1.status_code == 200

        response2 = client.get("/limited")
        assert response2.status_code == 200

    def test_rate_limit_exceeded_shows_error_message(self, app_dir: Path) -> None:
        """Rate limit exceeded re-renders form with rate_limit_error flag."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "form.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if rate_limit_error %}<div class="error">Too many requests</div>{% endif %}
{% if success %}<div class="success">Done!</div>{% endif %}
<form method="POST"><input name="data"></form>
{% endblock %}
""")

        (pages_dir / "_form.py").write_text("""
from zerojs import rate_limit

def get() -> dict:
    return {}

@rate_limit("1/minute")
def post() -> dict:
    return {"success": True}
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First POST succeeds
        response1 = client.post("/form", data={"data": "test"})
        assert response1.status_code == 200
        assert "Done!" in response1.text

        # Second POST shows rate limit error message
        response2 = client.post("/form", data={"data": "test"})
        assert response2.status_code == 429
        assert "Too many requests" in response2.text

    def test_rate_limit_resets_after_time_window(self, app_dir: Path) -> None:
        """Rate limit resets after the configured time window passes."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (pages_dir / "form.html").write_text("""
{% extends 'base.html' %}
{% block content %}
{% if rate_limit_error %}<div class="error">Too many requests</div>{% endif %}
{% if success %}<div class="success">Done!</div>{% endif %}
<form method="POST"><input name="data"></form>
{% endblock %}
""")

        (pages_dir / "_form.py").write_text("""
from zerojs import rate_limit

def get() -> dict:
    return {}

@rate_limit("1/minute")
def post() -> dict:
    return {"success": True}
""")

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "100/minute"
""")

        start_time = datetime.now(tz=timezone.utc)

        with time_machine.travel(start_time, tick=False) as traveller:
            app = ZeroJS(
                pages_dir=pages_dir,
                components_dir=app_dir / "components",
                errors_dir=app_dir / "errors",
                settings_file=app_dir / "settings.py",
            )
            client = TestClient(app.asgi_app)

            # First POST succeeds
            response1 = client.post("/form", data={"data": "test"})
            assert response1.status_code == 200
            assert "Done!" in response1.text

            # Second POST is rate limited
            response2 = client.post("/form", data={"data": "test"})
            assert response2.status_code == 429
            assert "Too many requests" in response2.text

            # Advance time by 61 seconds (past the 1 minute window)
            traveller.shift(timedelta(seconds=61))

            # Third POST should succeed (rate limit reset)
            response3 = client.post("/form", data={"data": "test"})
            assert response3.status_code == 200
            assert "Done!" in response3.text
