"""Response utilities for building HTTP responses."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from .renderer import Renderer
from .router import Route


def make_csrf_response(
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


def create_response_maker(
    csrf_token: str | None, token_name: str, cookie_secure: bool
) -> Callable[[str, int], HTMLResponse]:
    """Create a response maker function that sets CSRF cookie if needed."""

    def response_maker(html: str, status_code: int = 200) -> HTMLResponse:
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

    return response_maker


def render_htmx_component_or_page(
    request: Request,
    route: Route,
    context: dict[str, Any],
    default_status: int,
    make_response: Callable[[str, int], HTMLResponse],
    renderer: Renderer,
    components_dir: Path,
) -> HTMLResponse:
    """Render HTMX component if available, otherwise full page."""
    is_htmx = request.headers.get("HX-Request")

    if is_htmx:
        hx_target = request.headers.get("HX-Target")
        if hx_target:
            component_name = hx_target.lstrip("#").replace("-", "_")
            component_file = components_dir / f"{component_name}.html"
            if component_file.exists():
                html = renderer.render_component(component_file, context)
                return make_response(html, 200)

    html = renderer.render(route.file_path, context)
    status = 200 if is_htmx else default_status
    return make_response(html, status)


def handle_result(
    result: Any,
    request: Request,
    route: Route,
    path_params: dict[str, Any],
    csrf_token: str | None,
    make_response: Callable[[str, int], HTMLResponse],
    renderer: Renderer,
    components_dir: Path,
) -> Response:
    """Handle the result from a route handler."""
    if isinstance(result, Response):
        return result

    if isinstance(result, str):
        if result.startswith("/"):
            if request.headers.get("HX-Request"):
                return Response(content="", status_code=200, headers={"HX-Redirect": result})
            return RedirectResponse(url=result, status_code=303)
        return make_response(result, 200)

    if isinstance(result, dict):
        context = {**result, "request": request, "csrf_token": csrf_token, **path_params}
        return render_htmx_component_or_page(request, route, context, 200, make_response, renderer, components_dir)

    return make_response("OK", 200)
