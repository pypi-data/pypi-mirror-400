"""ZeroJS middleware - re-exports Starlette middlewares for convenience."""

# Secweb security headers middlewares (wrapped for type safety)
from Secweb.ContentSecurityPolicy import ContentSecurityPolicy as _ContentSecurityPolicy  # type: ignore[import-untyped]
from Secweb.CrossOriginEmbedderPolicy import (  # type: ignore[import-untyped]
    CrossOriginEmbedderPolicy as _CrossOriginEmbedderPolicy,
)
from Secweb.CrossOriginOpenerPolicy import (  # type: ignore[import-untyped]
    CrossOriginOpenerPolicy as _CrossOriginOpenerPolicy,
)
from Secweb.CrossOriginResourcePolicy import (  # type: ignore[import-untyped]
    CrossOriginResourcePolicy as _CrossOriginResourcePolicy,
)
from Secweb.ReferrerPolicy import ReferrerPolicy as _ReferrerPolicy  # type: ignore[import-untyped]
from Secweb.StrictTransportSecurity import HSTS as _HSTS  # type: ignore[import-untyped]
from Secweb.XContentTypeOptions import XContentTypeOptions as _XContentTypeOptions  # type: ignore[import-untyped]
from Secweb.XFrameOptions import XFrame as _XFrame  # type: ignore[import-untyped]
from starlette.middleware.base import BaseHTTPMiddleware as Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


# Typed wrappers for Secweb middlewares
class ContentSecurityPolicy(_ContentSecurityPolicy):
    """Content-Security-Policy header middleware."""

    pass


class CrossOriginEmbedderPolicy(_CrossOriginEmbedderPolicy):
    """Cross-Origin-Embedder-Policy header middleware."""

    pass


class CrossOriginOpenerPolicy(_CrossOriginOpenerPolicy):
    """Cross-Origin-Opener-Policy header middleware."""

    pass


class CrossOriginResourcePolicy(_CrossOriginResourcePolicy):
    """Cross-Origin-Resource-Policy header middleware."""

    pass


class HSTS(_HSTS):
    """Strict-Transport-Security header middleware."""

    pass


class ReferrerPolicy(_ReferrerPolicy):
    """Referrer-Policy header middleware."""

    pass


class XContentTypeOptions(_XContentTypeOptions):
    """X-Content-Type-Options header middleware."""

    pass


class XFrame(_XFrame):
    """X-Frame-Options header middleware."""

    pass


class SecurityHeadersMiddleware:
    """Marker class to enable all security headers from SECURITY_HEADERS setting.

    This is not a real middleware - it's a marker that tells ZeroJS to apply
    security headers based on the SECURITY_HEADERS configuration in settings.py.

    Usage in settings.py:
        MIDDLEWARE = [
            "zerojs.middleware.SecurityHeadersMiddleware",
            ...
        ]

        SECURITY_HEADERS = {
            "xframe": "DENY",
            "xcto": True,
            "hsts": {"max-age": 31536000},
            "csp": {"default-src": ["'self'"]},
        }
    """

    pass


class RateLimitMiddleware:
    """Marker class to enable rate limiting from RATE_LIMIT_* settings.

    This is not a real middleware - it's a marker that tells ZeroJS to apply
    rate limiting based on the RATE_LIMIT_* configuration in settings.py.

    Usage in settings.py:
        MIDDLEWARE = [
            "zerojs.middleware.RateLimitMiddleware",
            ...
        ]

        RATE_LIMIT_DEFAULT = "100/minute"  # Default limit for all routes
        RATE_LIMIT_STORAGE = "memory://"   # or "redis://localhost:6379"
        RATE_LIMIT_STRATEGY = "fixed-window"  # or "moving-window"
        RATE_LIMIT_HEADERS = True  # Include X-RateLimit-* headers

    Rate limit format: "{count}/{period}"
        - count: number of requests allowed
        - period: second, minute, hour, day (or s, m, h, d)
        - Examples: "100/minute", "1000/hour", "5/second"
    """

    pass


__all__ = [
    # Starlette middlewares
    "Middleware",
    "CORSMiddleware",
    "GZipMiddleware",
    "HTTPSRedirectMiddleware",
    "SessionMiddleware",
    "TrustedHostMiddleware",
    # Security headers (Secweb)
    "SecurityHeadersMiddleware",
    "ContentSecurityPolicy",
    "CrossOriginEmbedderPolicy",
    "CrossOriginOpenerPolicy",
    "CrossOriginResourcePolicy",
    "HSTS",
    "ReferrerPolicy",
    "XContentTypeOptions",
    "XFrame",
    # Rate limiting (slowapi)
    "RateLimitMiddleware",
]
