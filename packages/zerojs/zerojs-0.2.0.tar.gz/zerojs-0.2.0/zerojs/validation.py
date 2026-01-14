"""Validation utilities for path and form parameters."""

import inspect
import uuid
from collections.abc import Callable
from pathlib import Path, PurePath
from typing import Any, get_type_hints

from pydantic import BaseModel

from .security import is_safe_path_segment
from .types import UnsafePath, UnsafeStr


def get_form_param_info(func: Callable[..., Any]) -> tuple[str | None, type | None]:
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
        if param_type is dict or (hasattr(param_type, "__origin__") and param_type.__origin__ is dict):
            return param_name, dict

    return None, None


def convert_path_param(value: str, target_type: type) -> Any:
    """Convert a string path parameter to the target type.

    Args:
        value: The string value from the URL path.
        target_type: The expected type from the function signature.

    Returns:
        The converted value.

    Raises:
        ValueError: If the value cannot be converted to the target type.
    """
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    if target_type is bool:
        return value.lower() in ("true", "1", "yes")
    if target_type is uuid.UUID:
        return uuid.UUID(value)
    # UnsafePath opts out of path traversal validation
    if target_type is UnsafePath or (isinstance(target_type, type) and issubclass(target_type, UnsafePath)):
        return Path(value)
    if target_type is Path or (isinstance(target_type, type) and issubclass(target_type, PurePath)):
        if not is_safe_path_segment(value):
            raise ValueError("Path contains unsafe traversal sequences")
        return Path(value)
    # UnsafeStr opts out of path traversal validation
    if target_type is UnsafeStr or (isinstance(target_type, type) and issubclass(target_type, UnsafeStr)):
        return value
    # str is validated by default for path traversal protection
    if target_type is str:
        if not is_safe_path_segment(value):
            raise ValueError("Path contains unsafe traversal sequences")
    return value


def validate_handler_type_hints(
    func: Callable[..., Any],
    path_params: list[str],
    route_path: str,
) -> None:
    """Validate that handler has type hints for all path parameters.

    Args:
        func: The handler function to validate.
        path_params: List of path parameter names from the route.
        route_path: The route path for error messages.

    Raises:
        TypeError: If any path parameter is missing a type hint.
    """
    if not path_params:
        return

    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    missing = [param for param in path_params if param not in hints]
    if missing:
        raise TypeError(
            f"Handler '{func.__name__}' for route '{route_path}' is missing type hints "
            f"for path parameters: {', '.join(missing)}"
        )


def validate_path_params(
    func: Callable[..., Any],
    path_params: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str] | None]:
    """Validate and convert path parameters based on function type hints.

    Args:
        func: The handler function with type hints.
        path_params: The raw path parameters from the request.

    Returns:
        Tuple of (validated_params, errors).
        If errors is not None, validation failed.
    """
    hints = get_type_hints(func)

    validated: dict[str, Any] = {}
    errors: dict[str, str] = {}

    for param_name, value in path_params.items():
        param_type = hints.get(param_name, str)  # Default to str if no hint

        try:
            validated[param_name] = convert_path_param(value, param_type)
        except (ValueError, TypeError):
            errors[param_name] = f"Invalid value: expected {param_type.__name__}"

    return validated, errors if errors else None


def get_query_param_info(
    func: Callable[..., Any],
    path_params: list[str],
) -> dict[str, tuple[type, Any]]:
    """Get query parameter info from function signature.

    Args:
        func: The handler function to inspect.
        path_params: List of path parameter names to exclude.

    Returns:
        Dict mapping param_name -> (type, default_value).
        default_value is inspect.Parameter.empty if required.
    """
    sig = inspect.signature(func)
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    query_params: dict[str, tuple[type, Any]] = {}

    for param_name, param in sig.parameters.items():
        # Skip path params, self, cls
        if param_name in path_params or param_name in ("self", "cls"):
            continue

        param_type = hints.get(param_name, str)

        # Skip BaseModel params (form data)
        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
            continue
        # Skip dict params (raw form data)
        if param_type is dict or (hasattr(param_type, "__origin__") and param_type.__origin__ is dict):
            continue

        query_params[param_name] = (param_type, param.default)

    return query_params


def validate_query_params(
    func: Callable[..., Any],
    query_params: dict[str, Any],
    path_params: list[str],
) -> tuple[dict[str, Any], dict[str, str] | None]:
    """Validate and convert query parameters based on function type hints.

    Args:
        func: The handler function with type hints.
        query_params: The raw query parameters from the request.
        path_params: List of path parameter names to exclude.

    Returns:
        Tuple of (validated_params, errors).
        If errors is not None, validation failed.
    """
    param_info = get_query_param_info(func, path_params)

    validated: dict[str, Any] = {}
    errors: dict[str, str] = {}

    for param_name, (param_type, default) in param_info.items():
        value = query_params.get(param_name)

        # Handle missing params
        if value is None:
            if default is inspect.Parameter.empty:
                errors[param_name] = "Missing required query parameter"
            else:
                validated[param_name] = default
            continue

        # Convert type
        if param_type is str:
            validated[param_name] = value
            continue

        try:
            validated[param_name] = convert_path_param(value, param_type)
        except (ValueError, TypeError):
            errors[param_name] = f"Invalid value: expected {param_type.__name__}"

    return validated, errors if errors else None
