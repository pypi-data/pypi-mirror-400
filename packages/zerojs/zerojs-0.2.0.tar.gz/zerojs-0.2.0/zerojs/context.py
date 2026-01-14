"""Context building utilities for template rendering."""

from collections.abc import Callable
from typing import Any

from fastapi import Request

from .handlers import HandlerFunc, load_route_handlers
from .router import Route


def build_page_context(
    route: Route,
    file_handler: HandlerFunc | None,
    path_params: dict[str, Any],
    request: Request,
    csrf_token: str | None,
    context_providers: dict[str, Callable[..., dict[str, Any]]],
    query_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the context dictionary for rendering a page."""
    context: dict[str, Any] = {}
    query_params = query_params or {}

    if file_handler:
        result = file_handler(**path_params, **query_params)
        if isinstance(result, dict):
            context = result

    if route.url_path in context_providers:
        provider = context_providers[route.url_path]
        context.update(provider(**path_params, **query_params))

    context["request"] = request
    context.update(path_params)

    if csrf_token:
        context["csrf_token"] = csrf_token

    return context


def build_error_context(
    request: Request,
    route: Route,
    path_params: dict[str, Any],
    form_dict: dict[str, Any],
    csrf_token: str | None,
    **extra_context: Any,
) -> dict[str, Any]:
    """Build error context with GET handler data merged in."""
    context: dict[str, Any] = {
        "request": request,
        "values": form_dict,
        "csrf_token": csrf_token,
        **path_params,
        **extra_context,
    }

    get_handlers = load_route_handlers(route.context_file) if route.context_file else {}
    if "get" in get_handlers:
        get_result = get_handlers["get"](**path_params)
        if isinstance(get_result, dict):
            context = {**get_result, **context}

    return context
