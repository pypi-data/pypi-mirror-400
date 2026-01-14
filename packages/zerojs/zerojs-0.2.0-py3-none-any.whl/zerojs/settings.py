"""Settings loader for user configuration."""

import importlib.util
from pathlib import Path
from typing import Any

from .cache import CacheConfig, CacheStrategy


def load_user_settings(settings_file: Path | None = None) -> dict[str, Any]:
    """Load settings from user's settings.py file.

    Args:
        settings_file: Path to settings.py. If None, looks in current directory.

    Returns:
        Dictionary with settings. Defaults are used for missing values.
    """
    defaults: dict[str, Any] = {
        # Cache settings
        "CACHE_STRATEGY": "none",  # "none" | "ttl" | "incremental"
        "CACHE_TTL": 0,  # Default TTL in seconds
        "CACHE_ROUTES": {},  # Per-route overrides: {"/path": {"strategy": "...", "ttl": N}}
        # PyScript settings
        "PYSCRIPT_ENABLED": False,
        "PYSCRIPT_RUNTIME": "micropython",  # "micropython" | "pyodide"
        "PYSCRIPT_VERSION": "2025.10.1",
        # CSRF settings
        "CSRF_ENABLED": True,
        "CSRF_TOKEN_NAME": "csrf_token",
        "CSRF_EXEMPT_ROUTES": [],  # Routes that skip CSRF validation
        "CSRF_COOKIE_SECURE": False,  # Set to True in production (HTTPS only)
        # Middleware settings
        "MIDDLEWARE": [],  # List of middleware class paths
        # TrustedHostMiddleware settings
        "TRUSTED_HOSTS": ["*"],
        # CORSMiddleware settings
        "CORS_ALLOWED_ORIGINS": [],
        "CORS_ALLOWED_METHODS": ["GET"],
        "CORS_ALLOWED_HEADERS": [],
        "CORS_ALLOW_CREDENTIALS": False,
        "CORS_MAX_AGE": 600,
        # GZipMiddleware settings
        "GZIP_MINIMUM_SIZE": 500,
        # SessionMiddleware settings
        "SECRET_KEY": "",  # Required for SessionMiddleware
        "SESSION_COOKIE": "session",
        "SESSION_MAX_AGE": 1209600,  # 14 days
        "SESSION_SAME_SITE": "lax",
        "SESSION_HTTPS_ONLY": False,
        # SecurityHeadersMiddleware settings (Secweb)
        "SECURITY_HEADERS": {
            # Content-Security-Policy: {"default-src": ["'self'"], "script-src": ["'self'"]}
            "csp": None,
            # X-Frame-Options: "DENY" | "SAMEORIGIN"
            "xframe": "SAMEORIGIN",
            # Strict-Transport-Security: {"max-age": 31536000, "includeSubDomains": True, "preload": True}
            "hsts": None,
            # X-Content-Type-Options: True to enable "nosniff"
            "xcto": True,
            # Referrer-Policy: ["strict-origin-when-cross-origin"]
            "referrer": ["strict-origin-when-cross-origin"],
            # Cross-Origin-Opener-Policy: "same-origin" | "same-origin-allow-popups" | "unsafe-none"
            "coop": None,
            # Cross-Origin-Embedder-Policy: "require-corp" | "unsafe-none"
            "coep": None,
            # Cross-Origin-Resource-Policy: "same-site" | "same-origin" | "cross-origin"
            "corp": None,
        },
        # RateLimitMiddleware settings (slowapi)
        "RATE_LIMIT_DEFAULT": "100/minute",  # Default limit for all routes
        "RATE_LIMIT_STORAGE": "memory://",  # Storage backend: "memory://" or "redis://host:port"
        "RATE_LIMIT_STRATEGY": "fixed-window",  # "fixed-window" | "moving-window"
        "RATE_LIMIT_HEADERS": True,  # Include X-RateLimit-* headers in response
    }

    if settings_file is None:
        settings_file = Path("settings.py")

    if not settings_file.exists():
        return defaults

    try:
        spec = importlib.util.spec_from_file_location("settings", settings_file)
        if spec is None or spec.loader is None:
            return defaults

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract known settings
        result = defaults.copy()
        for key in defaults:
            if hasattr(module, key):
                result[key] = getattr(module, key)

        return result

    except Exception:
        return defaults


def get_cache_config(settings: dict[str, Any], url_path: str) -> CacheConfig:
    """Get cache configuration for a specific URL path.

    Args:
        settings: Loaded settings dictionary
        url_path: The URL path (e.g., "/users/1")

    Returns:
        CacheConfig for this route
    """
    cache_routes: dict[str, dict[str, Any]] = settings.get("CACHE_ROUTES", {})

    # Check for exact route match
    if url_path in cache_routes:
        route_config = cache_routes[url_path]
        return CacheConfig.from_dict(route_config)

    # Use global defaults
    strategy_str = settings.get("CACHE_STRATEGY", "none")
    try:
        strategy = CacheStrategy(strategy_str)
    except ValueError:
        strategy = CacheStrategy.NONE

    ttl = settings.get("CACHE_TTL", 0)

    # If strategy is none or ttl is 0, return no-cache config
    if strategy == CacheStrategy.NONE or (strategy != CacheStrategy.NONE and ttl <= 0):
        return CacheConfig.none()

    return CacheConfig(strategy=strategy, ttl=ttl)
