"""Component route registration for HTMX support."""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError
from starlette.responses import Response

from ..csrf import generate_csrf_token, validate_csrf_token
from ..handlers import HandlerFunc, MethodHandlers, load_route_handlers
from ..renderer import Renderer
from ..response import make_csrf_response
from ..validation import get_form_param_info, validate_query_params


def register_component_routes(
    fastapi: FastAPI,
    components_dir: Path,
    components_url: str | None,
    renderer: Renderer,
    settings: dict[str, Any],
) -> None:
    """Register routes for dynamic component loading (HTMX support)."""
    if not components_url or not components_dir.exists():
        return

    for component_file in components_dir.glob("*.html"):
        # Skip base templates (convention: files starting with _ are private)
        if component_file.stem.startswith("_"):
            continue

        _register_component_handler(fastapi, component_file, components_url, components_dir, renderer, settings)


def _register_component_handler(
    fastapi: FastAPI,
    component_file: Path,
    components_url: str,
    components_dir: Path,
    renderer: Renderer,
    settings: dict[str, Any],
) -> None:
    """Register a handler for a single component."""
    component_name = component_file.stem
    url_path = f"{components_url}/{component_name}"

    # Check for context file
    context_file = components_dir / f"_{component_name}.py"
    file_handlers: MethodHandlers = {}
    if context_file.exists():
        file_handlers = load_route_handlers(context_file)

    # Register GET handler
    get_handler = file_handlers.get("get")

    def handler(request: Request, _file: Path = component_file, _get: HandlerFunc | None = get_handler) -> HTMLResponse:
        # Validate and convert query params
        query_dict = dict(request.query_params)
        context: dict[str, Any] = {}

        if _get:
            query_params, query_errors = validate_query_params(_get, query_dict, [])
            if query_errors:
                context = {"request": request, "errors": query_errors}
                html = renderer.render_component(_file, context)
                return HTMLResponse(content=html, status_code=422)

            result = _get(**query_params)
            if isinstance(result, dict):
                context.update(result)
        else:
            context = query_dict

        context["request"] = request

        # Render component
        html = renderer.render_component(_file, context)
        return HTMLResponse(content=html)

    handler.__name__ = f"component_{component_name}"
    fastapi.get(url_path, response_class=HTMLResponse)(handler)

    # Register POST handler if exists
    if "post" in file_handlers:
        _register_component_post_handler(fastapi, component_file, url_path, file_handlers["post"], renderer, settings)


async def _validate_component_csrf(
    request: Request, url_path: str, settings: dict[str, Any]
) -> tuple[bool, dict[str, Any] | None]:
    """Validate CSRF token for component POST request.

    Returns:
        (is_valid, form_data_dict or None if validation was skipped)
    """
    csrf_enabled = settings.get("CSRF_ENABLED", True)
    csrf_exempt_routes: list[str] = settings.get("CSRF_EXEMPT_ROUTES", [])

    if not csrf_enabled or url_path in csrf_exempt_routes:
        return True, None

    token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")
    cookie_token = request.cookies.get(token_name)
    form_data = await request.form()
    form_token = form_data.get(token_name)

    is_valid = validate_csrf_token(cookie_token, str(form_token) if form_token else None)
    form_dict = {k: v for k, v in dict(form_data).items() if k != token_name}
    return is_valid, form_dict


def _parse_form_data(
    form_dict: dict[str, Any], form_param_name: str | None, form_param_type: type | None
) -> tuple[dict[str, Any], str | None]:
    """Parse form data, validating with Pydantic if needed.

    Returns:
        (kwargs dict, error_message or None)
    """
    if not form_param_name:
        return {}, None

    if form_param_type and issubclass(form_param_type, BaseModel):
        try:
            return {form_param_name: form_param_type(**form_dict)}, None
        except ValidationError as e:
            errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors() if err.get("loc")]
            return {}, "; ".join(errors) if errors else "Validation error"

    return {form_param_name: form_dict}, None


def _register_component_post_handler(
    fastapi: FastAPI,
    component_file: Path,
    url_path: str,
    post_handler: HandlerFunc,
    renderer: Renderer,
    settings: dict[str, Any],
) -> None:
    """Register a POST handler for a component."""
    form_param_name, form_param_type = get_form_param_info(post_handler)

    async def handler(request: Request) -> Response:
        csrf_enabled = settings.get("CSRF_ENABLED", True)
        token_name = settings.get("CSRF_TOKEN_NAME", "csrf_token")
        cookie_secure = settings.get("CSRF_COOKIE_SECURE", False)
        new_csrf_token = generate_csrf_token() if csrf_enabled else None

        # CSRF validation
        is_valid, csrf_form_dict = await _validate_component_csrf(request, url_path, settings)
        if not is_valid and csrf_form_dict is not None:
            csrf_context: dict[str, Any] = {
                "request": request,
                "csrf_error": True,
                "values": csrf_form_dict,
                "csrf_token": new_csrf_token,
            }
            html = renderer.render_component(component_file, csrf_context)
            return make_csrf_response(html, new_csrf_token, token_name, cookie_secure)

        # Parse form data
        query_dict = dict(request.query_params)
        form_data = await request.form()
        form_dict = {k: v for k, v in dict(form_data).items() if k != token_name}

        # Validate query params
        query_params, query_errors = validate_query_params(post_handler, query_dict, [])
        if query_errors:
            error_context: dict[str, Any] = {
                "request": request,
                "errors": query_errors,
                "csrf_token": new_csrf_token,
            }
            html = renderer.render_component(component_file, error_context)
            return make_csrf_response(html, new_csrf_token, token_name, cookie_secure, status_code=422)

        form_kwargs, error_msg = _parse_form_data(form_dict, form_param_name, form_param_type)
        if error_msg:
            return make_csrf_response(error_msg, new_csrf_token, token_name, cookie_secure, status_code=422)

        # Call handler
        result = post_handler(**query_params, **form_kwargs)

        if isinstance(result, Response):
            return result
        if isinstance(result, dict):
            context: dict[str, Any] = {**query_params, **result, "request": request, "csrf_token": new_csrf_token}
            html = renderer.render_component(component_file, context)
            return make_csrf_response(html, new_csrf_token, token_name, cookie_secure)

        return make_csrf_response(str(result) if result else "", new_csrf_token, token_name, cookie_secure)

    handler.__name__ = f"component_post_{component_file.stem}"
    fastapi.post(url_path)(handler)
