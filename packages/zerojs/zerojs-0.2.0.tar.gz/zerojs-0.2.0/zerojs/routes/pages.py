"""Page route registration."""

import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from ..cache import HTMLCache
from ..context import build_error_context, build_page_context
from ..csrf import generate_csrf_token, validate_csrf_token
from ..handlers import HandlerFunc, MethodHandlers, load_route_handlers
from ..renderer import Renderer
from ..response import create_response_maker, handle_result, render_htmx_component_or_page
from ..router import Route, scan_pages
from ..settings import get_cache_config
from ..validation import get_form_param_info, validate_handler_type_hints, validate_path_params, validate_query_params


def register_page_routes(
    fastapi: FastAPI,
    pages_dir: Path,
    components_dir: Path,
    renderer: Renderer,
    cache: HTMLCache,
    settings: dict[str, Any],
    context_providers: dict[str, Callable[..., dict[str, Any]]],
) -> None:
    """Scan pages directory and register all routes."""
    routes = scan_pages(pages_dir)

    for route in routes:
        _create_route_handler(fastapi, route, components_dir, renderer, cache, settings, context_providers)


def _create_route_handler(
    fastapi: FastAPI,
    route: Route,
    components_dir: Path,
    renderer: Renderer,
    cache: HTMLCache,
    settings: dict[str, Any],
    context_providers: dict[str, Callable[..., dict[str, Any]]],
) -> None:
    """Create and register route handlers for a page."""
    # Static files (.txt, .md) are served as plain text
    if route.is_static:
        _register_static_handler(fastapi, route)
        return

    # Load handlers from file if it exists
    file_handlers: MethodHandlers = {}
    if route.context_file:
        file_handlers = load_route_handlers(route.context_file)

    # Always register GET (renders the template)
    _register_get_handler(
        fastapi, route, file_handlers.get("get"), components_dir, renderer, cache, settings, context_providers
    )

    # Register other methods if handlers exist
    for method in ("post", "put", "patch", "delete"):
        if method in file_handlers:
            _register_method_handler(fastapi, route, method, file_handlers[method], components_dir, renderer, settings)


def _register_static_handler(fastapi: FastAPI, route: Route) -> None:
    """Register a handler for static text files (.txt, .md)."""
    # Determine content type
    content_types = {
        ".txt": "text/plain",
        ".md": "text/markdown",
    }
    content_type = content_types.get(route.file_path.suffix, "text/plain")

    def handler(request: Request) -> PlainTextResponse:
        content = route.file_path.read_text()
        return PlainTextResponse(content=content, media_type=content_type)

    handler.__name__ = f"static_{route.url_path.replace('/', '_').replace('.', '_')}"
    fastapi.get(route.url_path)(handler)


def _register_get_handler(
    fastapi: FastAPI,
    route: Route,
    file_handler: HandlerFunc | None,
    components_dir: Path,
    renderer: Renderer,
    cache: HTMLCache,
    settings: dict[str, Any],
    context_providers: dict[str, Callable[..., dict[str, Any]]],
) -> None:
    """Register a GET handler that renders the template."""
    # Validate type hints for path parameters at startup
    if file_handler and route.params:
        validate_handler_type_hints(file_handler, route.params, route.url_path)

    handler_rate_limit: str | None = getattr(file_handler, "_rate_limit", None) if file_handler else None

    _rate_limit_checker = None
    if handler_rate_limit and hasattr(fastapi.state, "limiter"):
        limiter = fastapi.state.limiter

        @limiter.limit(handler_rate_limit)
        async def _rate_limit_checker(request: Request) -> Response:
            return Response()

    def render_page(
        path_params: dict[str, Any],
        request: Request,
        csrf_token: str | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        context = build_page_context(
            route, file_handler, path_params, request, csrf_token, context_providers, query_params
        )
        return renderer.render(route.file_path, context)

    def background_rerender(cache_key: str, path_params: dict[str, Any], request: Request) -> None:
        html = render_page(path_params, request)
        cache.set(cache_key, html)

    async def handler(request: Request) -> HTMLResponse:
        if _rate_limit_checker:
            await _rate_limit_checker(request)

        path_params = dict(request.path_params)
        query_params: dict[str, Any] = {}

        # Validate path params based on handler type hints
        if file_handler:
            path_params, param_errors = validate_path_params(file_handler, path_params)
            if param_errors:
                context = {"request": request, "errors": param_errors, **path_params}
                html = renderer.render(route.file_path, context)
                return HTMLResponse(content=html, status_code=422)

            # Validate query params
            query_dict = dict(request.query_params)
            query_params, query_errors = validate_query_params(file_handler, query_dict, route.params)
            if query_errors:
                context = {"request": request, "errors": query_errors, **path_params}
                html = renderer.render(route.file_path, context)
                return HTMLResponse(content=html, status_code=422)

        csrf_token = generate_csrf_token() if settings.get("CSRF_ENABLED", True) else None
        token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")
        cookie_secure = settings.get("CSRF_COOKIE_SECURE", False)

        # Skip caching in dev mode
        if os.environ.get("ZEROJS_DEV_MODE"):
            html = render_page(path_params, request, csrf_token, query_params)
            return _make_csrf_response(html, csrf_token, token_name, cookie_secure)

        cache_key = str(request.url.path)
        config = get_cache_config(settings, cache_key)
        cache_result = cache.get(cache_key, config)

        cached_response = _handle_cached_response(
            cache_result, cache_key, cache, path_params, request, background_rerender
        )
        if cached_response:
            return cached_response

        html = render_page(path_params, request, csrf_token, query_params)

        if config.strategy.value != "none":
            cache.set(cache_key, html)

        return _make_csrf_response(html, csrf_token, token_name, cookie_secure)

    handler.__name__ = f"get_{route.url_path.replace('/', '_').replace('{', '').replace('}', '')}"
    fastapi.get(route.url_path, response_class=HTMLResponse)(handler)


def _handle_cached_response(
    cache_result: Any,
    cache_key: str,
    cache: HTMLCache,
    path_params: dict[str, Any],
    request: Request,
    render_func: Any,
) -> HTMLResponse | None:
    """Handle cached response, returning None if rendering is needed."""
    from starlette.background import BackgroundTask

    if not cache_result.html or cache_result.should_render:
        return None

    if cache_result.should_rerender_background:
        cache.mark_rerendering(cache_key)
        task = BackgroundTask(render_func, cache_key, path_params, request)
        return HTMLResponse(content=cache_result.html, background=task)

    return HTMLResponse(content=cache_result.html)


def _make_csrf_response(
    html: str, csrf_token: str | None, token_name: str, cookie_secure: bool, status_code: int = 200
) -> HTMLResponse:
    """Create an HTML response with CSRF cookie if token provided."""
    response = HTMLResponse(content=html, status_code=status_code)
    if csrf_token:
        response.set_cookie(
            key=token_name,
            value=csrf_token,
            httponly=True,
            samesite="strict",
            secure=cookie_secure,
        )
    return response


def _register_method_handler(
    fastapi: FastAPI,
    route: Route,
    method: str,
    file_handler: HandlerFunc,
    components_dir: Path,
    renderer: Renderer,
    settings: dict[str, Any],
) -> None:
    """Register a POST/PUT/PATCH/DELETE handler."""
    # Validate type hints for path parameters at startup
    if route.params:
        validate_handler_type_hints(file_handler, route.params, route.url_path)

    rate_limit_checker = _create_rate_limit_checker(fastapi, file_handler)
    form_param_name, form_param_type = get_form_param_info(file_handler)

    async def handler(request: Request) -> Response:
        raw_path_params = dict(request.path_params)

        # Validate path params based on handler type hints
        path_params, param_errors = validate_path_params(file_handler, raw_path_params)
        if param_errors:
            token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")
            cookie_secure = settings.get("CSRF_COOKIE_SECURE", False)
            new_csrf_token = generate_csrf_token() if settings.get("CSRF_ENABLED", True) else None
            make_response = create_response_maker(new_csrf_token, token_name, cookie_secure)
            # Build error context without calling GET handler (it may have same type hints)
            context: dict[str, Any] = {
                "request": request,
                "errors": param_errors,
                "csrf_token": new_csrf_token,
                **raw_path_params,
            }
            return render_htmx_component_or_page(request, route, context, 422, make_response, renderer, components_dir)

        token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")
        cookie_secure = settings.get("CSRF_COOKIE_SECURE", False)
        csrf_enabled = settings.get("CSRF_ENABLED", True)
        new_csrf_token = generate_csrf_token() if csrf_enabled else None

        make_response = create_response_maker(new_csrf_token, token_name, cookie_secure)

        # Validate query params
        query_dict = dict(request.query_params)
        query_params, query_errors = validate_query_params(file_handler, query_dict, route.params)
        if query_errors:
            query_error_ctx: dict[str, Any] = {
                "request": request,
                "errors": query_errors,
                "csrf_token": new_csrf_token,
                **path_params,
            }
            return render_htmx_component_or_page(
                request, route, query_error_ctx, 422, make_response, renderer, components_dir
            )

        kwargs: dict[str, Any] = {**path_params, **query_params}

        # CSRF validation
        csrf_valid, form_dict = await _validate_csrf(request, route, settings)
        if not csrf_valid:
            context = build_error_context(request, route, path_params, form_dict, new_csrf_token, csrf_error=True)
            return render_htmx_component_or_page(request, route, context, 403, make_response, renderer, components_dir)

        # Parse form data
        form_dict = await _get_form_dict(request, form_dict, form_param_name, token_name)
        parsed_value, errors = _parse_form_data_for_handler(form_dict, form_param_name, form_param_type)
        if errors:
            context = build_error_context(request, route, path_params, form_dict, new_csrf_token, errors=errors)
            return render_htmx_component_or_page(request, route, context, 422, make_response, renderer, components_dir)
        if form_param_name and parsed_value is not None:
            kwargs[form_param_name] = parsed_value

        # Rate limit check
        rate_limit_response = await _check_rate_limit(
            rate_limit_checker,
            request,
            route,
            path_params,
            form_dict,
            new_csrf_token,
            make_response,
            renderer,
            components_dir,
        )
        if rate_limit_response:
            return rate_limit_response

        result = file_handler(**kwargs)
        return handle_result(
            result, request, route, path_params, new_csrf_token, make_response, renderer, components_dir
        )

    handler.__name__ = f"{method}_{route.url_path.replace('/', '_').replace('{', '').replace('}', '')}"

    # Register with appropriate FastAPI method
    router_method = getattr(fastapi, method)
    router_method(route.url_path)(handler)


def _create_rate_limit_checker(
    fastapi: FastAPI, file_handler: HandlerFunc
) -> Callable[[Request], Awaitable[Response]] | None:
    """Create a rate limit checker if handler has rate limiting configured."""
    handler_rate_limit: str | None = getattr(file_handler, "_rate_limit", None)
    if not handler_rate_limit:
        return None
    if not hasattr(fastapi.state, "limiter"):
        return None

    limiter = fastapi.state.limiter

    @limiter.limit(handler_rate_limit)
    async def checker(request: Request) -> Response:
        return Response()

    return checker


async def _validate_csrf(
    request: Request,
    route: Route,
    settings: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """Validate CSRF token. Returns (is_valid, form_data_dict)."""
    csrf_enabled = settings.get("CSRF_ENABLED", True)
    csrf_exempt_routes: list[str] = settings.get("CSRF_EXEMPT_ROUTES", [])
    token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")

    if not csrf_enabled or route.url_path in csrf_exempt_routes:
        return True, {}

    cookie_token = request.cookies.get(token_name)
    form_data = await request.form()
    form_token = form_data.get(token_name)
    form_dict = {k: v for k, v in dict(form_data).items() if k != token_name}

    is_valid = validate_csrf_token(cookie_token, str(form_token) if form_token else None)
    return is_valid, form_dict


def _parse_form_data_for_handler(
    form_dict: dict[str, Any],
    form_param_name: str | None,
    form_param_type: type | None,
) -> tuple[Any | None, dict[str, str] | None]:
    """Parse form data for handler. Returns (parsed_value, validation_errors)."""
    if not form_param_name:
        return None, None

    if form_param_type and issubclass(form_param_type, BaseModel):
        try:
            return form_param_type(**form_dict), None
        except ValidationError as e:
            errors = {str(err["loc"][0]): err["msg"] for err in e.errors()}
            return None, errors

    return form_dict, None


async def _get_form_dict(
    request: Request, form_dict: dict[str, Any], form_param_name: str | None, token_name: str
) -> dict[str, Any]:
    """Get form dictionary, parsing from request if needed."""
    if form_param_name and not form_dict:
        form_data = await request.form()
        return {k: v for k, v in dict(form_data).items() if k != token_name}
    return form_dict


async def _check_rate_limit(
    rate_limit_checker: Callable[[Request], Awaitable[Response]] | None,
    request: Request,
    route: Route,
    path_params: dict[str, Any],
    form_dict: dict[str, Any],
    csrf_token: str | None,
    make_response: Callable[[str, int], HTMLResponse],
    renderer: Renderer,
    components_dir: Path,
) -> Response | None:
    """Check rate limit and return error response if exceeded, None otherwise."""
    if not rate_limit_checker:
        return None
    try:
        await rate_limit_checker(request)
        return None
    except RateLimitExceeded:
        context = build_error_context(request, route, path_params, form_dict, csrf_token, rate_limit_error=True)
        return render_htmx_component_or_page(request, route, context, 429, make_response, renderer, components_dir)
