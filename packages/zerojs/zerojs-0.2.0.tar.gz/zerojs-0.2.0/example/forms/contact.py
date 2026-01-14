"""Contact form definition."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactForm(BaseModel):
    """Contact form with various field types."""

    name: str = Field(title="Your Name")
    email: EmailStr = Field(title="Email Address")
    subject: Literal["general", "support", "sales"] = Field(
        title="Subject",
        json_schema_extra={
            "choices": {
                "general": "General Inquiry",
                "support": "Technical Support",
                "sales": "Sales Question",
            }
        },
    )
    message: str = Field(title="Message", json_schema_extra={"textarea": True})

    @classmethod
    @field_validator("name")
    def name_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @classmethod
    @field_validator("message")
    def message_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message is required")
        if len(v.strip()) < 10:
            raise ValueError("Message must be at least 10 characters")
        return v.strip()
