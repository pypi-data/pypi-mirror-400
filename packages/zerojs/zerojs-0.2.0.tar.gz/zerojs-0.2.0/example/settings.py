"""ZeroJS settings for the example application."""

# Cache strategy: "none" | "ttl" | "incremental"
# - none: No caching (default)
# - ttl: Hard expiration after TTL seconds
# - incremental: Serve stale content, re-render in background (ISR)
CACHE_STRATEGY = "none"

# Default cache TTL in seconds
CACHE_TTL = 0

# Per-route cache configuration overrides
# Each route can have its own strategy and TTL
CACHE_ROUTES = {
    "/": {"strategy": "ttl", "ttl": 60},  # Home page: TTL cache for 1 minute
    "/about": {"strategy": "ttl", "ttl": 3600},  # About page: TTL cache for 1 hour
    # "/users/{id}": {"strategy": "incremental", "ttl": 30},  # User pages: ISR
}

# PyScript settings for client-side Python
PYSCRIPT_ENABLED = True
PYSCRIPT_RUNTIME = "micropython"  # "micropython" (300KB) or "pyodide" (11MB)
PYSCRIPT_VERSION = "2025.10.1"

# Middleware configuration (Django-style, order matters)
# Available: CORSMiddleware, GZipMiddleware, TrustedHostMiddleware, HTTPSRedirectMiddleware, RateLimitMiddleware
MIDDLEWARE = [
    "zerojs.middleware.RateLimitMiddleware",
    "zerojs.middleware.GZipMiddleware",
]

# Rate limiting settings
RATE_LIMIT_DEFAULT = "100/minute"  # Global default (can be overridden per-route with @rate_limit)

# GZip settings
GZIP_MINIMUM_SIZE = 500  # Compress responses larger than 500 bytes
