"""Handler loading utilities."""

import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeAlias

HTTP_METHODS = ("get", "post", "put", "patch", "delete")

HandlerFunc: TypeAlias = Callable[..., dict[str, Any]]
MethodHandlers: TypeAlias = dict[str, HandlerFunc]


def load_route_handlers(context_file: Path) -> MethodHandlers:
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
