"""CSRF protection utilities for ZeroJS."""

import hmac
import secrets

from markupsafe import Markup


def generate_csrf_token(length: int = 32) -> str:
    """Generate a cryptographically secure CSRF token.

    Args:
        length: Number of bytes for the token (default: 32, produces 64 hex chars)

    Returns:
        A secure random hex string
    """
    return secrets.token_hex(length)


def validate_csrf_token(cookie_token: str | None, form_token: str | None) -> bool:
    """Validate CSRF token using constant-time comparison.

    Args:
        cookie_token: Token from the cookie
        form_token: Token from the form submission

    Returns:
        True if tokens match, False otherwise
    """
    if not cookie_token or not form_token:
        return False
    return hmac.compare_digest(cookie_token, form_token)


def csrf_input(token: str, token_name: str = "csrf_token") -> Markup:
    """Generate a hidden input field with the CSRF token.

    Args:
        token: The CSRF token value
        token_name: Name attribute for the input field

    Returns:
        Safe HTML markup for the hidden input
    """
    return Markup(f'<input type="hidden" name="{token_name}" value="{token}">')
