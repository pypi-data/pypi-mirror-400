"""Decorators for ZeroJS route handlers."""

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


def rate_limit(limit: str) -> Callable[[F], F]:
    """Decorator to apply rate limiting to a route handler.

    Usage:
        from zerojs import rate_limit

        @rate_limit("5/minute")
        def post(data: ContactForm) -> dict:
            return {"success": True}

    Args:
        limit: Rate limit string in format "{count}/{period}".
            - count: number of requests allowed
            - period: second, minute, hour, day (or s, m, h, d)
            - Examples: "5/minute", "100/hour", "10/second"

    The decorator marks the function with the limit, which ZeroJS
    applies when registering the route. The user's handler does not
    need to receive the request object.
    """

    def decorator(func: F) -> F:
        func._rate_limit = limit  # type: ignore[attr-defined]
        return func

    return decorator
