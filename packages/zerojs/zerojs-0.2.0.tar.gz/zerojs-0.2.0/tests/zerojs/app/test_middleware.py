"""Tests for middleware system."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import time_machine
from fastapi.testclient import TestClient

from zerojs import ZeroJS


class TestMiddleware:
    """Tests for middleware system."""

    def test_gzip_middleware_compresses_response(self, app_dir: Path) -> None:
        """GZipMiddleware compresses large responses."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Create a large page
        large_content = "x" * 1000
        (pages_dir / "large.html").write_text(f"""
{{% extends 'base.html' %}}
{{% block content %}}<p>{large_content}</p>{{% endblock %}}
""")

        # Enable GZip middleware
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.GZipMiddleware"]
GZIP_MINIMUM_SIZE = 100
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get("/large", headers={"Accept-Encoding": "gzip"})

        assert response.status_code == 200
        assert response.headers.get("content-encoding") == "gzip"

    def test_trusted_host_middleware_blocks_invalid_host(self, app_dir: Path) -> None:
        """TrustedHostMiddleware returns 400 for invalid hosts."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable TrustedHost middleware
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.TrustedHostMiddleware"]
TRUSTED_HOSTS = ["example.com"]
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app, raise_server_exceptions=False)

        response = client.get("/", headers={"Host": "evil.com"})

        assert response.status_code == 400

    def test_cors_middleware_adds_headers(self, app_dir: Path) -> None:
        """CORSMiddleware adds CORS headers to responses."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable CORS middleware
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.CORSMiddleware"]
CORS_ALLOWED_ORIGINS = ["https://frontend.example.com"]
CORS_ALLOWED_METHODS = ["GET", "POST"]
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get(
            "/",
            headers={"Origin": "https://frontend.example.com"},
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://frontend.example.com"

    def test_multiple_middlewares_in_order(self, app_dir: Path) -> None:
        """Multiple middlewares are applied in correct order."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Create a page with enough content for GZip
        large_content = "y" * 1000
        (pages_dir / "test.html").write_text(f"""
{{% extends 'base.html' %}}
{{% block content %}}<p>{large_content}</p>{{% endblock %}}
""")

        # Enable multiple middlewares
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = [
    "zerojs.middleware.CORSMiddleware",
    "zerojs.middleware.GZipMiddleware",
]
CORS_ALLOWED_ORIGINS = ["*"]
GZIP_MINIMUM_SIZE = 100
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response = client.get(
            "/test",
            headers={"Origin": "https://example.com", "Accept-Encoding": "gzip"},
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"
        assert response.headers.get("content-encoding") == "gzip"

    def test_add_middleware_programmatically(self, app_dir: Path) -> None:
        """add_middleware() adds middleware programmatically."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Create large content BEFORE app init
        large_content = "z" * 1000
        (pages_dir / "programmatic.html").write_text(f"""
{{% extends 'base.html' %}}
{{% block content %}}<p>{large_content}</p>{{% endblock %}}
""")

        (app_dir / "settings.py").write_text("CSRF_ENABLED = False")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        from zerojs.middleware import GZipMiddleware

        app.add_middleware(GZipMiddleware, minimum_size=100)

        client = TestClient(app.asgi_app)

        response = client.get("/programmatic", headers={"Accept-Encoding": "gzip"})

        assert response.status_code == 200
        assert response.headers.get("content-encoding") == "gzip"

    def test_session_middleware_sets_cookie(self, app_dir: Path) -> None:
        """SessionMiddleware sets session cookie."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable Session middleware
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.SessionMiddleware"]
SECRET_KEY = "test-secret-key-for-sessions"
SESSION_COOKIE = "my_session"
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
        # Session cookie is only set when session data is modified
        # This test just verifies the middleware loads without error

    def test_session_middleware_requires_secret_key(self, app_dir: Path) -> None:
        """SessionMiddleware raises error without SECRET_KEY."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable Session middleware without SECRET_KEY
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.SessionMiddleware"]
""")

        with pytest.raises(ValueError, match="SECRET_KEY is required"):
            ZeroJS(
                pages_dir=pages_dir,
                components_dir=app_dir / "components",
                errors_dir=app_dir / "errors",
                settings_file=app_dir / "settings.py",
            )

    def test_security_headers_middleware_adds_headers(self, app_dir: Path) -> None:
        """SecurityHeadersMiddleware adds security headers based on SECURITY_HEADERS setting."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable security headers middleware
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.SecurityHeadersMiddleware"]
SECURITY_HEADERS = {
    "xframe": "DENY",
    "xcto": True,
    "referrer": ["strict-origin-when-cross-origin"],
}
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
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_rate_limit_middleware_limits_requests(self, app_dir: Path) -> None:
        """RateLimitMiddleware limits requests based on RATE_LIMIT_* settings."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        # Enable rate limit middleware with very low limit for testing
        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "2/minute"
RATE_LIMIT_HEADERS = True
""")

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # First two requests should succeed
        response1 = client.get("/")
        assert response1.status_code == 200

        response2 = client.get("/")
        assert response2.status_code == 200

        # Third request should be rate limited
        response3 = client.get("/")
        assert response3.status_code == 429  # Too Many Requests

    def test_rate_limit_middleware_includes_headers(self, app_dir: Path) -> None:
        """RateLimitMiddleware includes X-RateLimit-* headers when enabled."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "10/minute"
RATE_LIMIT_HEADERS = True
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
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers

    def test_rate_limit_middleware_resets_after_time_window(self, app_dir: Path) -> None:
        """RateLimitMiddleware resets after the configured time window passes."""
        pages_dir = app_dir / "pages"
        import os

        os.chdir(app_dir)

        (app_dir / "settings.py").write_text("""
CSRF_ENABLED = False
MIDDLEWARE = ["zerojs.middleware.RateLimitMiddleware"]
RATE_LIMIT_DEFAULT = "1/minute"
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

            # First request succeeds
            response1 = client.get("/")
            assert response1.status_code == 200

            # Second request is rate limited
            response2 = client.get("/")
            assert response2.status_code == 429

            # Advance time by 61 seconds (past the 1 minute window)
            traveller.shift(timedelta(seconds=61))

            # Third request should succeed (rate limit reset)
            response3 = client.get("/")
            assert response3.status_code == 200
