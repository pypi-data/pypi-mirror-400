"""Form rendering utilities for Pydantic models."""

from pathlib import Path
from typing import Any, Literal, get_args, get_origin

from jinja2 import pass_context
from markupsafe import Markup
from pydantic import BaseModel
from pydantic.fields import FieldInfo

# Path to built-in form shadow component
FORM_SHADOW_TEMPLATE = Path(__file__).parent / "templates" / "zerojs" / "components" / "form.shadow.html"


def _get_input_type(field_type: type, field_info: FieldInfo) -> str:
    """Determine HTML input type from Python type and field metadata."""
    # Check json_schema_extra for explicit type override
    extra = field_info.json_schema_extra
    if extra and isinstance(extra, dict) and extra.get("textarea"):
        return "textarea"

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
        choices = extra["choices"]
        if isinstance(choices, dict):
            return choices  # type: ignore[return-value]
    # Use literal values as both key and label
    return {v: v for v in literal_values}


def _render_select_input(
    name: str,
    label: str,
    field_type: type,
    field_info: FieldInfo,
    value: Any,
    invalid_class: str,
    required_attr: str,
    error_html: str,
) -> str:
    """Render a select input field."""
    literal_values = _get_literal_values(field_type)
    choices = _get_choices(field_info, literal_values)

    options = ['<option value="">-- Select --</option>']
    for val, display in choices.items():
        selected = "selected" if str(value) == str(val) else ""
        options.append(f'<option value="{val}" {selected}>{display}</option>')

    options_html = "\n            ".join(options)
    return f"""<div class="form__field form__field--select">
    <label class="form__label" for="{name}">{label}</label>
    <select class="form__input form__input--select{invalid_class}" id="{name}" name="{name}" {required_attr}>
        {options_html}
    </select>
    {error_html}
</div>"""


def _render_checkbox_input(name: str, label: str, value: Any, invalid_class: str, error_html: str) -> str:
    """Render a checkbox input field."""
    checked = "checked" if value else ""
    return f"""<div class="form__field form__field--checkbox">
    <input class="form__input form__input--checkbox{invalid_class}" type="checkbox" id="{name}" name="{name}" {checked}>
    <label class="form__label" for="{name}">{label}</label>
    {error_html}
</div>"""


def _render_textarea_input(
    name: str,
    label: str,
    value: Any,
    placeholder: str,
    invalid_class: str,
    required_attr: str,
    error_html: str,
) -> str:
    """Render a textarea input field."""
    placeholder_attr = f'placeholder="{placeholder}"' if placeholder else ""
    textarea_class = f"form__input form__input--textarea{invalid_class}"
    textarea_attrs = f'id="{name}" name="{name}" {placeholder_attr} {required_attr}'.strip()
    return f"""<div class="form__field form__field--textarea">
    <label class="form__label" for="{name}">{label}</label>
    <textarea class="{textarea_class}" {textarea_attrs}>{value or ""}</textarea>
    {error_html}
</div>"""


def _render_standard_input(
    name: str,
    label: str,
    input_type: str,
    field_type: type,
    value: Any,
    placeholder: str,
    invalid_class: str,
    required_attr: str,
    error_html: str,
) -> str:
    """Render a standard input field (text, email, number, etc.)."""
    step_attr = 'step="any"' if field_type is float else ""
    value_attr = f'value="{value}"' if value is not None else ""
    placeholder_attr = f'placeholder="{placeholder}"' if placeholder else ""
    input_attrs = (
        f'type="{input_type}" id="{name}" name="{name}" {value_attr} {placeholder_attr} {required_attr} {step_attr}'
    ).strip()

    return f"""<div class="form__field">
    <label class="form__label" for="{name}">{label}</label>
    <input class="form__input{invalid_class}" {input_attrs}>
    {error_html}
</div>"""


def _render_input(
    name: str,
    field_type: type,
    field_info: FieldInfo,
    value: Any,
    error: str | None,
) -> str:
    """Render a single form input with BEM classes."""
    input_type = _get_input_type(field_type, field_info)
    label = field_info.title or name.replace("_", " ").title()
    placeholder = field_info.description or ""
    required_attr = "required" if field_info.is_required() else ""
    invalid_class = " form__input--invalid" if error else ""
    error_html = f'<span class="form__error">{error}</span>' if error else ""

    if _is_select_field(field_type):
        return _render_select_input(
            name, label, field_type, field_info, value, invalid_class, required_attr, error_html
        )

    if input_type == "checkbox":
        return _render_checkbox_input(name, label, value, invalid_class, error_html)

    if input_type == "textarea":
        return _render_textarea_input(name, label, value, placeholder, invalid_class, required_attr, error_html)

    return _render_standard_input(
        name, label, input_type, field_type, value, placeholder, invalid_class, required_attr, error_html
    )


def _render_form(
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
    csrf_token: str | None = None,
    success_message: str | None = None,
    error_message: str | None = None,
) -> str:
    """Render form content with BEM classes (without Shadow DOM wrapper)."""
    values = values or {}
    errors = errors or {}

    # Build form attributes
    attrs = ['class="form"', f'method="{method}"']
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

    # Render alert messages
    alerts_html = ""
    if success_message:
        alerts_html += f'<div class="form__alert form__alert--success" role="status">{success_message}</div>\n'
    if error_message:
        alerts_html += f'<div class="form__alert form__alert--error" role="alert">{error_message}</div>\n'

    # Render fields
    fields_html = []

    # Add CSRF token as hidden field
    if csrf_token:
        csrf_field = (
            f'<div class="form__field form__field--hidden">'
            f'<input type="hidden" name="csrf_token" value="{csrf_token}"></div>'
        )
        fields_html.append(csrf_field)

    for name, field_info in form_class.model_fields.items():
        field_type = field_info.annotation or str
        value = values.get(name)
        error = errors.get(name)

        field_html = _render_input(name, field_type, field_info, value, error)
        fields_html.append(field_html)

    fields_str = "\n".join(fields_html)

    return f"""<form {attrs_str}>
{alerts_html}{fields_str}
<button class="form__submit" type="submit">{submit_text}</button>
</form>"""


@pass_context
def render_form(
    context: dict[str, Any],
    form_class: type[BaseModel],
    method: str = "POST",
    action: str = "",
    submit_text: str = "Submit",
    form_id: str | None = None,
    hx_post: str | None = None,
    hx_target: str | None = None,
    hx_swap: str | None = None,
    csrf_token: str | None = None,
    success_message: str | None = None,
    error_message: str | None = None,
) -> Markup:
    """Render a Pydantic model as an HTML form inside a Shadow DOM component.

    Uses BEM naming convention for CSS classes. The form is wrapped in
    a shadow DOM boundary for style encapsulation.

    Args:
        context: Jinja2 context (auto-injected)
        form_class: Pydantic model class to render
        method: HTTP method (GET, POST)
        action: Form action URL
        submit_text: Text for submit button
        form_id: Optional form ID attribute
        hx_post: HTMX hx-post attribute
        hx_target: HTMX hx-target attribute
        hx_swap: HTMX hx-swap attribute
        csrf_token: CSRF token (auto-injected from context)
        success_message: Optional success message to display
        error_message: Optional error message to display (e.g., rate limit, CSRF)

    Returns:
        Markup: Safe HTML string with shadow DOM wrapper
    """
    # Auto-inject values and errors from context
    values = context.get("values")
    errors = context.get("errors")

    # Auto-inject csrf_token from context if not provided
    if csrf_token is None:
        csrf_token = context.get("csrf_token")

    # Auto-inject error messages from context
    if error_message is None:
        if context.get("csrf_error"):
            error_message = "Your previous session expired. Please try again."
        elif context.get("rate_limit_error"):
            error_message = "Too many requests. Please wait a moment and try again."

    # Render form content with BEM classes
    form_content = _render_form(
        form_class=form_class,
        values=values,
        errors=errors,
        method=method,
        action=action,
        submit_text=submit_text,
        form_id=form_id,
        hx_post=hx_post,
        hx_target=hx_target,
        hx_swap=hx_swap,
        csrf_token=csrf_token,
        success_message=success_message,
        error_message=error_message,
    )

    # Read shadow component template and inject form content
    shadow_template = FORM_SHADOW_TEMPLATE.read_text()
    shadow_html = shadow_template.replace("{{ form_content }}", form_content)

    # Wrap in shadow DOM (same as ShadowDOMLoader does for .shadow.html files)
    return Markup(f"""<zjs-form>
    <template shadowrootmode="open">
{shadow_html}
    </template>
</zjs-form>""")
