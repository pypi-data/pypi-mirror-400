"""Handlers for /users/{id} route."""

from forms import UserForm

# Fake user database
USERS = {
    "1": {"name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
    "2": {"name": "Bob Smith", "email": "bob@example.com", "role": "User"},
    "3": {"name": "Charlie Brown", "email": "charlie@example.com", "role": "Editor"},
}


def get(id: str) -> dict:
    """Handle GET request - provide context for the template."""
    user = USERS.get(id, {"name": "Unknown", "email": "N/A", "role": "N/A"})
    return {"user": user}


def post(id: str, data: UserForm) -> dict:
    """Handle POST request - update user and show success."""
    if id in USERS:
        USERS[id]["name"] = data.name
        USERS[id]["email"] = data.email
    return {"user": USERS.get(id, {}), "success": True}
