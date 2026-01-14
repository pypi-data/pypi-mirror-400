"""Form rendering utilities for Pydantic models."""

from typing import Any, get_args, get_origin, Literal
from markupsafe import Markup
from pydantic import BaseModel
from pydantic.fields import FieldInfo


def _get_input_type(field_type: type, field_info: FieldInfo) -> str:
    """Determine HTML input type from Python type."""
    type_name = getattr(field_type, "__name__", str(field_type))

    # Check for EmailStr
    if type_name == "EmailStr":
        return "email"

    # Check for SecretStr
    if type_name == "SecretStr":
        return "password"

    # Basic types
    if field_type is bool:
        return "checkbox"
    if field_type is int:
        return "number"
    if field_type is float:
        return "number"

    # Date types
    if type_name == "date":
        return "date"
    if type_name == "datetime":
        return "datetime-local"

    return "text"


def _is_select_field(field_type: type) -> bool:
    """Check if field should render as select."""
    origin = get_origin(field_type)
    return origin is Literal


def _get_literal_values(field_type: type) -> list[str]:
    """Extract values from Literal type."""
    return list(get_args(field_type))


def _get_choices(field_info: FieldInfo, literal_values: list[str]) -> dict[str, str]:
    """Get choices dict from field info or use literal values."""
    extra = field_info.json_schema_extra
    if extra and isinstance(extra, dict) and "choices" in extra:
        return extra["choices"]
    # Use literal values as both key and label
    return {v: v for v in literal_values}


def _render_input(
    name: str,
    field_type: type,
    field_info: FieldInfo,
    value: Any,
    error: str | None,
) -> str:
    """Render a single form input."""
    input_type = _get_input_type(field_type, field_info)

    # Get label from field title or name
    label = field_info.title or name.replace("_", " ").title()

    # Get placeholder from description
    placeholder = field_info.description or ""

    # Check if required
    is_required = field_info.is_required()
    required_attr = "required" if is_required else ""

    # Error class
    error_class = "error" if error else ""

    # Handle select fields
    if _is_select_field(field_type):
        literal_values = _get_literal_values(field_type)
        choices = _get_choices(field_info, literal_values)

        options = []
        for val, display in choices.items():
            selected = "selected" if str(value) == str(val) else ""
            options.append(f'<option value="{val}" {selected}>{display}</option>')

        options_html = "\n".join(options)
        return f"""<div class="form-field">
    <label for="{name}">{label}</label>
    <select id="{name}" name="{name}" class="{error_class}" {required_attr}>
        <option value="">-- Select --</option>
        {options_html}
    </select>
    {f'<span class="error-message">{error}</span>' if error else ''}
</div>"""

    # Handle checkbox
    if input_type == "checkbox":
        checked = "checked" if value else ""
        return f"""<div class="form-field">
    <label>
        <input type="checkbox" id="{name}" name="{name}" {checked} class="{error_class}">
        {label}
    </label>
    {f'<span class="error-message">{error}</span>' if error else ''}
</div>"""

    # Handle textarea (multiline strings)
    extra = field_info.json_schema_extra
    if extra and isinstance(extra, dict) and extra.get("textarea"):
        return f"""<div class="form-field">
    <label for="{name}">{label}</label>
    <textarea id="{name}" name="{name}" placeholder="{placeholder}" class="{error_class}" {required_attr}>{value or ''}</textarea>
    {f'<span class="error-message">{error}</span>' if error else ''}
</div>"""

    # Handle number step for floats
    step_attr = 'step="any"' if field_type is float else ""

    # Standard input
    value_attr = f'value="{value}"' if value is not None else ""
    return f"""<div class="form-field">
    <label for="{name}">{label}</label>
    <input type="{input_type}" id="{name}" name="{name}" {value_attr} placeholder="{placeholder}" class="{error_class}" {required_attr} {step_attr}>
    {f'<span class="error-message">{error}</span>' if error else ''}
</div>"""


def render_form(
    form_class: type[BaseModel],
    values: dict[str, Any] | None = None,
    errors: dict[str, str] | None = None,
    method: str = "POST",
    action: str = "",
    submit_text: str = "Submit",
    form_id: str | None = None,
    hx_post: str | None = None,
    hx_target: str | None = None,
    hx_swap: str | None = None,
) -> Markup:
    """Render a Pydantic model as an HTML form.

    Args:
        form_class: Pydantic model class to render
        values: Pre-filled values (e.g., from failed validation)
        errors: Validation errors by field name
        method: HTTP method (GET, POST)
        action: Form action URL
        submit_text: Text for submit button
        form_id: Optional form ID attribute
        hx_post: HTMX hx-post attribute
        hx_target: HTMX hx-target attribute
        hx_swap: HTMX hx-swap attribute

    Returns:
        Markup: Safe HTML string
    """
    values = values or {}
    errors = errors or {}

    # Build form attributes
    attrs = [f'method="{method}"']
    if action:
        attrs.append(f'action="{action}"')
    if form_id:
        attrs.append(f'id="{form_id}"')
    if hx_post:
        attrs.append(f'hx-post="{hx_post}"')
    if hx_target:
        attrs.append(f'hx-target="{hx_target}"')
    if hx_swap:
        attrs.append(f'hx-swap="{hx_swap}"')

    attrs_str = " ".join(attrs)

    # Render fields
    fields_html = []
    for name, field_info in form_class.model_fields.items():
        field_type = field_info.annotation
        value = values.get(name)
        error = errors.get(name)

        field_html = _render_input(name, field_type, field_info, value, error)
        fields_html.append(field_html)

    fields_str = "\n".join(fields_html)

    return Markup(f"""<form {attrs_str}>
{fields_str}
<div class="form-field">
    <button type="submit">{submit_text}</button>
</div>
</form>""")
