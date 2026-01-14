"""User form definition."""

from typing import Any

from pydantic import BaseModel, EmailStr, ValidationError, field_validator


class UserForm(BaseModel):
    """Form data for updating a user."""

    name: str
    email: EmailStr

    @classmethod
    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name is required")
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip()

    @classmethod
    @field_validator("email", mode="wrap")
    def email_custom_message(cls, v: Any, handler: Any) -> str:
        """Wrap EmailStr validation with custom error message."""
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError("Email is required")
        try:
            return handler(v)
        except ValidationError:
            raise ValueError("Please enter a valid email (e.g. user@example.com)")
