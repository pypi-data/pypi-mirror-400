"""Main ZeroJS application class."""

import importlib.util
import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any, get_type_hints

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .cache import CacheConfig, HTMLCache
from .constants import DEFAULT_404, DEFAULT_500
from .renderer import Renderer
from .router import Route, scan_pages
from .settings import get_cache_config, load_user_settings


HTTP_METHODS = ("get", "post", "put", "patch", "delete")

type HandlerFunc = Callable[..., dict[str, Any]]
type MethodHandlers = dict[str, HandlerFunc]


def _get_form_param_info(func: Callable[..., Any]) -> tuple[str | None, type | None]:
    """Get form parameter name and type from function signature.

    Returns:
        (param_name, param_type) where:
        - param_type is a BaseModel subclass for validation
        - param_type is dict for raw form data
        - param_type is None if no form param expected
    """
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    sig = inspect.signature(func)

    for param_name, param in sig.parameters.items():
        # Skip path params (they come from URL)
        if param_name in ("self", "cls"):
            continue

        param_type = hints.get(param_name, param.annotation)

        # Check if it's a BaseModel subclass
        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
            return param_name, param_type

        # Check if it's explicitly typed as dict (for raw form)
        if param_type is dict or (
            hasattr(param_type, "__origin__") and param_type.__origin__ is dict
        ):
            return param_name, dict

    return None, None


def _load_route_handlers(context_file: Path) -> MethodHandlers:
    """Dynamically load handler functions from a Python file.

    Looks for functions named: get, post, put, patch, delete
    Falls back to 'context' for backwards compatibility with GET.
    """
    spec = importlib.util.spec_from_file_location(context_file.stem, context_file)
    if spec is None or spec.loader is None:
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    handlers: MethodHandlers = {}

    # Load method-specific handlers
    for method in HTTP_METHODS:
        fn = getattr(module, method, None)
        if callable(fn):
            handlers[method] = fn

    # Backwards compatibility: 'context' function maps to 'get'
    if "get" not in handlers:
        context_fn = getattr(module, "context", None)
        if callable(context_fn):
            handlers["get"] = context_fn

    return handlers


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
        self._cache = HTMLCache()

        self._fastapi = FastAPI(**fastapi_kwargs)
        self._renderer = Renderer(
            self.pages_dir, self.components_dir, self.errors_dir, self._settings
        )
        self._context_providers: dict[str, Callable[..., dict[str, Any]]] = {}

        self._mount_static()
        self._register_error_handlers()
        self._register_routes()
        self._register_component_routes()

    @property
    def asgi_app(self) -> FastAPI:
        """Return the underlying FastAPI app for ASGI servers."""
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

        if reload:
            # Find the module and app variable name from the call stack
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_globals = frame.f_back.f_globals
                module_name = caller_globals.get("__name__", "__main__")

                # Find the variable name that holds this ZeroJS instance
                app_var = None
                for name, value in caller_globals.items():
                    if value is self:
                        app_var = name
                        break

                if module_name == "__main__":
                    # Get the actual module name from __file__
                    import os
                    file_path = caller_globals.get("__file__", "")
                    module_name = os.path.splitext(os.path.basename(file_path))[0]

                if app_var:
                    uvicorn.run(
                        f"{module_name}:{app_var}.asgi_app",
                        host=host,
                        port=port,
                        reload=True,
                        reload_includes=["*.html", "*.css", "*.js", "*.py"],
                    )
                    return

        # Non-reload mode: run directly
        uvicorn.run(self._fastapi, host=host, port=port)

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
        if status_code == 404:
            return DEFAULT_404
        return DEFAULT_500

    def _register_error_handlers(self) -> None:
        """Register custom error handlers for 404 and 500."""

        @self._fastapi.exception_handler(StarletteHTTPException)
        async def http_exception_handler(
            request: Request, exc: StarletteHTTPException
        ) -> HTMLResponse:
            status_code = exc.status_code
            if status_code in (404, 500):
                html = self._render_error_page(status_code, request)
                return HTMLResponse(content=html, status_code=status_code)
            return HTMLResponse(
                content=f"<h1>{status_code} Error</h1>",
                status_code=status_code,
            )

        @self._fastapi.exception_handler(Exception)
        async def general_exception_handler(
            request: Request, exc: Exception
        ) -> HTMLResponse:
            html = self._render_error_page(500, request)
            return HTMLResponse(content=html, status_code=500)

    def _register_routes(self) -> None:
        """Scan pages directory and register routes."""
        routes = scan_pages(self.pages_dir)

        for route in routes:
            self._create_route_handler(route)

    def _register_component_routes(self) -> None:
        """Register routes for dynamic component loading (HTMX support)."""
        if not self.components_url or not self.components_dir.exists():
            return

        for component_file in self.components_dir.glob("*.html"):
            # Skip base templates (convention: files starting with _ are private)
            if component_file.stem.startswith("_"):
                continue

            self._register_component_handler(component_file)

    def _register_component_handler(self, component_file: Path) -> None:
        """Register a handler for a single component."""
        component_name = component_file.stem
        url_path = f"{self.components_url}/{component_name}"

        # Check for context file
        context_file = self.components_dir / f"_{component_name}.py"
        file_handlers: MethodHandlers = {}
        if context_file.exists():
            file_handlers = _load_route_handlers(context_file)

        # Register GET handler
        get_handler = file_handlers.get("get")

        async def handler(request: Request, _file: Path = component_file, _get: HandlerFunc | None = get_handler) -> HTMLResponse:
            # Get query params as context
            context: dict[str, Any] = dict(request.query_params)

            # Call file handler if exists
            if _get:
                result = _get(**context)
                if isinstance(result, dict):
                    context.update(result)

            context["request"] = request

            # Render component
            html = self._renderer.render_component(_file, context)
            return HTMLResponse(content=html)

        handler.__name__ = f"component_{component_name}"
        self._fastapi.get(url_path, response_class=HTMLResponse)(handler)

        # Register POST handler if exists
        if "post" in file_handlers:
            self._register_component_post_handler(component_file, url_path, file_handlers["post"])

    def _register_component_post_handler(
        self, component_file: Path, url_path: str, post_handler: HandlerFunc
    ) -> None:
        """Register a POST handler for a component."""
        from fastapi.responses import Response

        # Detect form parameter type
        form_param_name, form_param_type = _get_form_param_info(post_handler)

        async def handler(request: Request) -> Response:
            # Parse form data only if handler expects it
            query_params = dict(request.query_params)
            kwargs: dict[str, Any] = {**query_params}

            if form_param_name:
                form_data = await request.form()
                form_dict = dict(form_data)

                if form_param_type and issubclass(form_param_type, BaseModel):
                    # Validate with Pydantic
                    try:
                        kwargs[form_param_name] = form_param_type(**form_dict)
                    except ValidationError as e:
                        return HTMLResponse(content=str(e), status_code=422)
                else:
                    # Pass raw dict
                    kwargs[form_param_name] = form_dict

            result = post_handler(**kwargs)

            if isinstance(result, Response):
                return result
            if isinstance(result, dict):
                context: dict[str, Any] = {**query_params, **result, "request": request}
                html = self._renderer.render_component(component_file, context)
                return HTMLResponse(content=html)

            return HTMLResponse(content=str(result) if result else "")

        handler.__name__ = f"component_post_{component_file.stem}"
        self._fastapi.post(url_path)(handler)

    def _create_route_handler(self, route: Route) -> None:
        """Create and register route handlers for a page."""
        # Static files (.txt, .md) are served as plain text
        if route.is_static:
            self._register_static_handler(route)
            return

        # Load handlers from file if it exists
        file_handlers: MethodHandlers = {}
        if route.context_file:
            file_handlers = _load_route_handlers(route.context_file)

        # Always register GET (renders the template)
        self._register_get_handler(route, file_handlers.get("get"))

        # Register other methods if handlers exist
        for method in ("post", "put", "patch", "delete"):
            if method in file_handlers:
                self._register_method_handler(route, method, file_handlers[method])

    def _register_static_handler(self, route: Route) -> None:
        """Register a handler for static text files (.txt, .md)."""
        from fastapi.responses import PlainTextResponse

        # Determine content type
        content_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
        }
        content_type = content_types.get(route.file_path.suffix, "text/plain")

        async def handler(request: Request) -> PlainTextResponse:
            content = route.file_path.read_text()
            return PlainTextResponse(content=content, media_type=content_type)

        handler.__name__ = f"static_{route.url_path.replace('/', '_').replace('.', '_')}"
        self._fastapi.get(route.url_path)(handler)

    def _register_get_handler(
        self, route: Route, file_handler: HandlerFunc | None
    ) -> None:
        """Register a GET handler that renders the template."""
        from starlette.background import BackgroundTask

        # Capture references for closure
        _cache = self._cache
        _settings = self._settings
        _renderer = self._renderer
        _context_providers = self._context_providers

        def render_page(path_params: dict, request: Request) -> str:
            """Render the page with context."""
            context: dict[str, Any] = {}
            if file_handler:
                result = file_handler(**path_params)
                if isinstance(result, dict):
                    context = result

            if route.url_path in _context_providers:
                provider = _context_providers[route.url_path]
                context.update(provider(**path_params))

            context["request"] = request
            context.update(path_params)

            return _renderer.render(route.file_path, context)

        def background_rerender(cache_key: str, path_params: dict, request: Request) -> None:
            """Re-render page in background and update cache."""
            html = render_page(path_params, request)
            _cache.set(cache_key, html)

        async def handler(request: Request) -> HTMLResponse:
            path_params = dict(request.path_params)
            cache_key = str(request.url.path)

            # Get cache config and check cache
            config = get_cache_config(_settings, cache_key)
            cache_result = _cache.get(cache_key, config)

            # If we have cached HTML and don't need to render
            if cache_result.html and not cache_result.should_render:
                # For incremental: trigger background re-render if stale
                if cache_result.should_rerender_background:
                    _cache.mark_rerendering(cache_key)
                    task = BackgroundTask(background_rerender, cache_key, path_params, request)
                    return HTMLResponse(content=cache_result.html, background=task)
                return HTMLResponse(content=cache_result.html)

            # Need to render
            html = render_page(path_params, request)

            # Cache if strategy is not 'none'
            if config.strategy.value != "none":
                _cache.set(cache_key, html)

            return HTMLResponse(content=html)

        handler.__name__ = f"get_{route.url_path.replace('/', '_').replace('{', '').replace('}', '')}"
        self._fastapi.get(route.url_path, response_class=HTMLResponse)(handler)

    def _register_method_handler(
        self, route: Route, method: str, file_handler: HandlerFunc
    ) -> None:
        """Register a POST/PUT/PATCH/DELETE handler."""
        from fastapi.responses import RedirectResponse, Response

        # Detect form parameter type
        form_param_name, form_param_type = _get_form_param_info(file_handler)

        async def handler(request: Request) -> Response:
            path_params = dict(request.path_params)
            kwargs: dict[str, Any] = {**path_params}

            # Parse form data only if handler expects it
            if form_param_name:
                form_data = await request.form()
                form_dict = dict(form_data)

                if form_param_type and issubclass(form_param_type, BaseModel):
                    # Validate with Pydantic
                    try:
                        kwargs[form_param_name] = form_param_type(**form_dict)
                    except ValidationError as e:
                        # Re-render form with errors
                        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
                        context: dict[str, Any] = {
                            "request": request,
                            "errors": errors,
                            "values": form_dict,
                            **path_params,
                        }
                        # Call GET handler to get additional context
                        get_handlers = _load_route_handlers(route.context_file) if route.context_file else {}
                        if "get" in get_handlers:
                            get_result = get_handlers["get"](**path_params)
                            if isinstance(get_result, dict):
                                # errors and values should override get_result
                                context = {**get_result, **context}

                        is_htmx = request.headers.get("HX-Request")

                        # For HTMX requests, try to render just the target component
                        if is_htmx:
                            hx_target = request.headers.get("HX-Target")
                            if hx_target:
                                # Try to render a component matching the target id
                                # e.g., hx-target="#user-form" -> user_form.html
                                component_name = hx_target.lstrip("#").replace("-", "_")
                                component_file = self.components_dir / f"{component_name}.html"
                                if component_file.exists():
                                    html = self._renderer.render_component(component_file, context)
                                    return HTMLResponse(content=html, status_code=200)

                        # Render full page
                        # Use 200 for HTMX (so content gets swapped), 422 for regular requests
                        html = self._renderer.render(route.file_path, context)
                        status = 200 if is_htmx else 422
                        return HTMLResponse(content=html, status_code=status)
                else:
                    # Pass raw dict
                    kwargs[form_param_name] = form_dict

            result = file_handler(**kwargs)

            # Handle different return types
            if isinstance(result, Response):
                return result
            if isinstance(result, str):
                # String starting with / is a redirect
                if result.startswith("/"):
                    # Check if request is from HTMX
                    if request.headers.get("HX-Request"):
                        # For HTMX requests, use HX-Redirect header for full page navigation
                        return Response(
                            content="",
                            status_code=200,
                            headers={"HX-Redirect": result},
                        )
                    return RedirectResponse(url=result, status_code=303)
                return HTMLResponse(content=result)
            if isinstance(result, dict):
                context = {**result, "request": request, **path_params}

                # For HTMX requests, try to render just the target component
                if request.headers.get("HX-Request"):
                    hx_target = request.headers.get("HX-Target")
                    if hx_target:
                        component_name = hx_target.lstrip("#").replace("-", "_")
                        component_file = self.components_dir / f"{component_name}.html"
                        if component_file.exists():
                            html = self._renderer.render_component(component_file, context)
                            return HTMLResponse(content=html)

                # Fallback: render full page
                html = self._renderer.render(route.file_path, context)
                return HTMLResponse(content=html)

            return HTMLResponse(content="OK")

        handler.__name__ = f"{method}_{route.url_path.replace('/', '_').replace('{', '').replace('}', '')}"

        # Register with appropriate FastAPI method
        router_method = getattr(self._fastapi, method)
        router_method(route.url_path)(handler)
