"""Handlers for /contact route."""

from forms import ContactForm

from zerojs import rate_limit


def get() -> dict:
    """GET /contact - show empty form."""
    return {"ContactForm": ContactForm}


@rate_limit("1/minute")
def post(data: ContactForm) -> dict:
    """POST /contact - process form submission.

    Rate limited to 1 submission per minute to prevent spam.
    """
    # In a real app, send email or save to database
    print(f"Contact form submitted: {data.name} <{data.email}> - {data.subject}")
    return {"ContactForm": ContactForm, "success": True}
