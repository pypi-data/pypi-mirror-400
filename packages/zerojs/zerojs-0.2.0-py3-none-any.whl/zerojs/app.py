"""Main ZeroJS application class."""

import importlib.util
import inspect
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from .cache import HTMLCache
from .constants import DEFAULT_403, DEFAULT_404, DEFAULT_500
from .renderer import Renderer
from .routes import register_component_routes, register_page_routes
from .settings import load_user_settings


class ZeroJS:
    """FastAPI wrapper with file-based routing."""

    def __init__(
        self,
        pages_dir: str | Path = "pages",
        components_dir: str | Path = "components",
        static_dir: str | Path = "static",
        static_url: str = "/static",
        errors_dir: str | Path = "errors",
        components_url: str | None = "/components",
        settings_file: str | Path | None = None,
        **fastapi_kwargs: Any,
    ) -> None:
        self.pages_dir = Path(pages_dir)
        self.components_dir = Path(components_dir)
        self.static_dir = Path(static_dir)
        self.static_url = static_url
        self.errors_dir = Path(errors_dir)
        self.components_url = components_url

        # Load user settings
        settings_path = Path(settings_file) if settings_file else None
        self._settings = load_user_settings(settings_path)
        self._settings["STATIC_URL"] = static_url
        self._cache = HTMLCache()

        self._fastapi = FastAPI(**fastapi_kwargs)
        self._register_middleware()  # Must be before routes

        self._renderer = Renderer(self.pages_dir, self.components_dir, self.errors_dir, self._settings)
        self._context_providers: dict[str, Callable[..., dict[str, Any]]] = {}

        self._mount_static()
        self._register_error_handlers()
        self._register_routes()

    @property
    def asgi_app(self) -> FastAPI:
        """Return the underlying FastAPI app for ASGI servers."""
        return self._fastapi

    @property
    def fastapi(self) -> FastAPI:
        """Return the underlying FastAPI app."""
        return self._fastapi

    def clear_cache(self) -> None:
        """Clear all cached HTML pages."""
        self._cache.clear()

    def invalidate_cache(self, url_path: str) -> None:
        """Invalidate cache for a specific URL.

        Args:
            url_path: The URL path to invalidate (e.g., "/users/1")
        """
        self._cache.invalidate(url_path)

    def add_middleware(self, middleware_class: type[Any], **kwargs: Any) -> None:
        """Add middleware programmatically.

        Args:
            middleware_class: The middleware class to add
            **kwargs: Arguments to pass to the middleware
        """
        self._fastapi.add_middleware(middleware_class, **kwargs)  # type: ignore[arg-type]

    def context(self, path: str) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
        """Decorator to register a context provider for a route.

        Example:
            @app.context("/users/{id}")
            def user_context(id: str):
                return {"user": get_user(id)}
        """

        def decorator(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
            self._context_providers[path] = func
            return func

        return decorator

    def start(
        self,
        host: str = "127.0.0.1",
        port: int = 3000,
        reload: bool = False,
    ) -> None:
        """Start the development server.

        Args:
            host: Host to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 3000)
            reload: Enable auto-reload on file changes (default: False)
        """
        import uvicorn

        if not reload:
            uvicorn.run(self._fastapi, host=host, port=port)
            return

        os.environ["ZEROJS_DEV_MODE"] = "1"
        self._warn_missing_watchfiles()

        frame = inspect.currentframe()
        if not frame or not frame.f_back:
            uvicorn.run(self._fastapi, host=host, port=port)
            return

        caller_globals = frame.f_back.f_globals
        app_var = self._find_app_variable(caller_globals)
        if not app_var:
            uvicorn.run(self._fastapi, host=host, port=port)
            return

        module_name = self._resolve_module_name(caller_globals)
        uvicorn.run(
            f"{module_name}:{app_var}.asgi_app",
            host=host,
            port=port,
            reload=True,
            reload_includes=["*.html", "*.css", "*.js", "*.py"],
        )

    # -------------------------------------------------------------------------
    # Private: Middleware
    # -------------------------------------------------------------------------

    def _register_middleware(self) -> None:
        """Load and register middleware from settings."""
        middleware_list: list[str] = self._settings.get("MIDDLEWARE", [])

        # Reverse order: first in list = outermost = executes first
        for middleware_path in reversed(middleware_list):
            middleware_class = self._import_middleware(middleware_path)

            # Special handling for SecurityHeadersMiddleware
            if middleware_class.__name__ == "SecurityHeadersMiddleware":
                self._register_security_headers()
                continue

            # Special handling for RateLimitMiddleware
            if middleware_class.__name__ == "RateLimitMiddleware":
                self._register_rate_limit()
                continue

            kwargs = self._get_middleware_kwargs(middleware_class)
            self._fastapi.add_middleware(middleware_class, **kwargs)  # type: ignore[arg-type]

    def _import_middleware(self, path: str) -> type[Any]:
        """Import middleware class from dotted path."""
        import importlib

        module_path, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def _get_middleware_kwargs(self, middleware_class: type[Any]) -> dict[str, Any]:
        """Get kwargs for built-in middleware based on settings."""
        name = middleware_class.__name__

        if name == "CORSMiddleware":
            return {
                "allow_origins": self._settings.get("CORS_ALLOWED_ORIGINS", []),
                "allow_methods": self._settings.get("CORS_ALLOWED_METHODS", ["GET"]),
                "allow_headers": self._settings.get("CORS_ALLOWED_HEADERS", []),
                "allow_credentials": self._settings.get("CORS_ALLOW_CREDENTIALS", False),
                "max_age": self._settings.get("CORS_MAX_AGE", 600),
            }
        elif name == "TrustedHostMiddleware":
            return {
                "allowed_hosts": self._settings.get("TRUSTED_HOSTS", ["*"]),
            }
        elif name == "GZipMiddleware":
            return {
                "minimum_size": self._settings.get("GZIP_MINIMUM_SIZE", 500),
            }
        elif name == "HTTPSRedirectMiddleware":
            return {}
        elif name == "SessionMiddleware":
            secret_key = self._settings.get("SECRET_KEY", "")
            if not secret_key:
                raise ValueError("SECRET_KEY is required for SessionMiddleware")
            return {
                "secret_key": secret_key,
                "session_cookie": self._settings.get("SESSION_COOKIE", "session"),
                "max_age": self._settings.get("SESSION_MAX_AGE", 1209600),
                "same_site": self._settings.get("SESSION_SAME_SITE", "lax"),
                "https_only": self._settings.get("SESSION_HTTPS_ONLY", False),
            }

        # Custom middleware: pass settings dict
        return {"settings": self._settings}

    def _register_security_headers(self) -> None:
        """Register security headers middleware based on SECURITY_HEADERS setting."""
        from .middleware import (
            HSTS,
            ContentSecurityPolicy,
            CrossOriginEmbedderPolicy,
            CrossOriginOpenerPolicy,
            CrossOriginResourcePolicy,
            ReferrerPolicy,
            XContentTypeOptions,
            XFrame,
        )

        headers = self._settings.get("SECURITY_HEADERS", {})

        # X-Content-Type-Options (nosniff)
        if headers.get("xcto"):
            self._fastapi.add_middleware(XContentTypeOptions)  # type: ignore[arg-type]

        # X-Frame-Options
        xframe = headers.get("xframe")
        if xframe:
            self._fastapi.add_middleware(XFrame, Option=xframe)  # type: ignore[arg-type]

        # Strict-Transport-Security (HSTS)
        hsts = headers.get("hsts")
        if hsts:
            self._fastapi.add_middleware(HSTS, Option=hsts)  # type: ignore[arg-type]

        # Content-Security-Policy
        csp = headers.get("csp")
        if csp:
            self._fastapi.add_middleware(ContentSecurityPolicy, Option=csp)  # type: ignore[arg-type]

        # Referrer-Policy
        referrer = headers.get("referrer")
        if referrer:
            self._fastapi.add_middleware(ReferrerPolicy, Option=referrer)  # type: ignore[arg-type]

        # Cross-Origin-Opener-Policy
        coop = headers.get("coop")
        if coop:
            self._fastapi.add_middleware(CrossOriginOpenerPolicy, Option=coop)  # type: ignore[arg-type]

        # Cross-Origin-Embedder-Policy
        coep = headers.get("coep")
        if coep:
            self._fastapi.add_middleware(CrossOriginEmbedderPolicy, Option=coep)  # type: ignore[arg-type]

        # Cross-Origin-Resource-Policy
        corp = headers.get("corp")
        if corp:
            self._fastapi.add_middleware(CrossOriginResourcePolicy, Option=corp)  # type: ignore[arg-type]

    def _register_rate_limit(self) -> None:
        """Register rate limiting middleware based on RATE_LIMIT_* settings."""
        from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore[import-untyped]
        from slowapi.middleware import SlowAPIMiddleware  # type: ignore[import-untyped]
        from slowapi.util import get_remote_address  # type: ignore[import-untyped]

        default_limit = self._settings.get("RATE_LIMIT_DEFAULT", "100/minute")
        storage_uri = self._settings.get("RATE_LIMIT_STORAGE", "memory://")
        strategy = self._settings.get("RATE_LIMIT_STRATEGY", "fixed-window")
        headers_enabled = self._settings.get("RATE_LIMIT_HEADERS", True)

        # Create limiter with settings
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[default_limit],
            storage_uri=storage_uri,
            strategy=strategy,
            headers_enabled=headers_enabled,
        )

        # Store limiter in app state (required by slowapi)
        self._fastapi.state.limiter = limiter

        # Add exception handler for rate limit exceeded
        self._fastapi.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

        # Add the middleware
        self._fastapi.add_middleware(SlowAPIMiddleware)  # type: ignore[arg-type]

    # -------------------------------------------------------------------------
    # Private: Dev Server Helpers
    # -------------------------------------------------------------------------

    def _warn_missing_watchfiles(self) -> None:
        """Warn if watchfiles is not installed for full hot reload support."""
        if not importlib.util.find_spec("watchfiles"):
            import warnings

            warnings.warn(
                "watchfiles not installed. Hot reload will only detect Python file changes. "
                "Install with: pip install zerojs[dev]",
                stacklevel=3,
            )

    def _find_app_variable(self, caller_globals: dict[str, Any]) -> str | None:
        """Find the variable name that holds this ZeroJS instance."""
        for name, value in caller_globals.items():
            if value is self:
                return name
        return None

    def _resolve_module_name(self, caller_globals: dict[str, Any]) -> str:
        """Resolve the module name from caller globals."""
        module_name = caller_globals.get("__name__", "__main__")
        if module_name == "__main__":
            file_path = caller_globals.get("__file__", "")
            module_name = os.path.splitext(os.path.basename(file_path))[0]
        return module_name

    # -------------------------------------------------------------------------
    # Private: Static Files & Error Handlers
    # -------------------------------------------------------------------------

    def _mount_static(self) -> None:
        """Mount static files directory if it exists."""
        if self.static_dir.exists():
            self._fastapi.mount(
                self.static_url,
                StaticFiles(directory=self.static_dir),
                name="static",
            )

    def _render_error_page(self, status_code: int, request: Request) -> str:
        """Render an error page if it exists, otherwise return default."""
        error_file = self.errors_dir / f"{status_code}.html"
        if error_file.exists():
            return self._renderer.render_file(error_file, {"request": request})
        if status_code == 403:
            return DEFAULT_403
        if status_code == 404:
            return DEFAULT_404
        return DEFAULT_500

    def _register_error_handlers(self) -> None:
        """Register custom error handlers for 404 and 500."""

        @self._fastapi.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> HTMLResponse:
            status_code = exc.status_code
            if status_code in (404, 500):
                html = self._render_error_page(status_code, request)
                return HTMLResponse(content=html, status_code=status_code)
            return HTMLResponse(
                content=f"<h1>{status_code} Error</h1>",
                status_code=status_code,
            )

        @self._fastapi.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception) -> HTMLResponse:
            html = self._render_error_page(500, request)
            return HTMLResponse(content=html, status_code=500)

    # -------------------------------------------------------------------------
    # Private: Route Registration
    # -------------------------------------------------------------------------

    def _register_routes(self) -> None:
        """Register all page and component routes."""
        register_page_routes(
            self._fastapi,
            self.pages_dir,
            self.components_dir,
            self._renderer,
            self._cache,
            self._settings,
            self._context_providers,
        )

        register_component_routes(
            self._fastapi,
            self.components_dir,
            self.components_url,
            self._renderer,
            self._settings,
        )
