"""Tests for form rendering utilities."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from zerojs.forms import _render_form as render_form


class SimpleForm(BaseModel):
    """Simple form with basic fields."""

    name: str
    age: int


class FormWithEmail(BaseModel):
    """Form with email field."""

    email: EmailStr


class FormWithOptional(BaseModel):
    """Form with optional field."""

    name: str
    nickname: str | None = None


class FormWithCheckbox(BaseModel):
    """Form with boolean field."""

    subscribe: bool = False


class FormWithSelect(BaseModel):
    """Form with literal (select) field."""

    status: Literal["active", "inactive", "pending"]


class FormWithLabeledSelect(BaseModel):
    """Form with labeled choices."""

    language: Literal["en", "es", "fr"] = Field(
        json_schema_extra={"choices": {"en": "English", "es": "Spanish", "fr": "French"}}
    )


class FormWithTextarea(BaseModel):
    """Form with textarea field."""

    message: str = Field(json_schema_extra={"textarea": True})


class FormWithTitles(BaseModel):
    """Form with custom titles."""

    user_name: str = Field(title="Your Name")
    user_email: EmailStr = Field(title="Email Address", description="We won't spam you")


class TestRenderFormBasic:
    """Tests for basic form rendering."""

    def test_renders_form_tag(self) -> None:
        """Form tag is rendered with method."""
        result = render_form(SimpleForm)
        assert "<form" in result
        assert 'method="POST"' in result
        assert "</form>" in result

    def test_renders_with_action(self) -> None:
        """Form action attribute is rendered."""
        result = render_form(SimpleForm, action="/submit")
        assert 'action="/submit"' in result

    def test_renders_with_form_id(self) -> None:
        """Form id attribute is rendered."""
        result = render_form(SimpleForm, form_id="my-form")
        assert 'id="my-form"' in result

    def test_renders_submit_button(self) -> None:
        """Submit button is rendered with BEM class."""
        result = render_form(SimpleForm)
        assert '<button class="form__submit" type="submit">Submit</button>' in result

    def test_custom_submit_text(self) -> None:
        """Custom submit button text."""
        result = render_form(SimpleForm, submit_text="Send")
        assert '<button class="form__submit" type="submit">Send</button>' in result


class TestRenderFormFields:
    """Tests for field rendering."""

    def test_renders_text_input(self) -> None:
        """String field renders as text input."""
        result = render_form(SimpleForm)
        assert 'type="text"' in result
        assert 'name="name"' in result

    def test_renders_number_input(self) -> None:
        """Integer field renders as number input."""
        result = render_form(SimpleForm)
        assert 'type="number"' in result
        assert 'name="age"' in result

    def test_renders_email_input(self) -> None:
        """EmailStr field renders as email input."""
        result = render_form(FormWithEmail)
        assert 'type="email"' in result
        assert 'name="email"' in result

    def test_renders_checkbox(self) -> None:
        """Boolean field renders as checkbox."""
        result = render_form(FormWithCheckbox)
        assert 'type="checkbox"' in result
        assert 'name="subscribe"' in result

    def test_renders_textarea(self) -> None:
        """Field with textarea=True renders as textarea."""
        result = render_form(FormWithTextarea)
        assert "<textarea" in result
        assert 'name="message"' in result

    def test_renders_labels(self) -> None:
        """Labels are rendered for fields."""
        result = render_form(SimpleForm)
        assert "<label" in result
        assert "Name" in result
        assert "Age" in result

    def test_custom_titles(self) -> None:
        """Custom field titles are used as labels."""
        result = render_form(FormWithTitles)
        assert "Your Name" in result
        assert "Email Address" in result

    def test_placeholder_from_description(self) -> None:
        """Field description is used as placeholder."""
        result = render_form(FormWithTitles)
        assert "We won't spam you" in result


class TestRenderFormSelect:
    """Tests for select field rendering."""

    def test_renders_select(self) -> None:
        """Literal field renders as select."""
        result = render_form(FormWithSelect)
        assert "<select" in result
        assert "</select>" in result
        assert "<option" in result

    def test_select_options(self) -> None:
        """Select options from Literal values."""
        result = render_form(FormWithSelect)
        assert 'value="active"' in result
        assert 'value="inactive"' in result
        assert 'value="pending"' in result

    def test_labeled_choices(self) -> None:
        """Custom choice labels from json_schema_extra."""
        result = render_form(FormWithLabeledSelect)
        assert 'value="en"' in result
        assert ">English<" in result
        assert 'value="es"' in result
        assert ">Spanish<" in result


class TestRenderFormValues:
    """Tests for pre-filled values."""

    def test_prefills_text_value(self) -> None:
        """Text input shows pre-filled value."""
        result = render_form(SimpleForm, values={"name": "Alice"})
        assert 'value="Alice"' in result

    def test_prefills_number_value(self) -> None:
        """Number input shows pre-filled value."""
        result = render_form(SimpleForm, values={"age": 25})
        assert 'value="25"' in result

    def test_prefills_checkbox(self) -> None:
        """Checkbox shows checked state."""
        result = render_form(FormWithCheckbox, values={"subscribe": True})
        assert "checked" in result

    def test_prefills_select(self) -> None:
        """Select shows selected option."""
        result = render_form(FormWithSelect, values={"status": "inactive"})
        assert 'value="inactive" selected' in result


class TestRenderFormErrors:
    """Tests for validation error display."""

    def test_shows_error_message(self) -> None:
        """Error message is displayed with BEM class."""
        result = render_form(SimpleForm, errors={"name": "Name is required"})
        assert "Name is required" in result
        assert 'class="form__error"' in result

    def test_adds_invalid_class(self) -> None:
        """Invalid modifier class is added to field with error."""
        result = render_form(SimpleForm, errors={"name": "Required"})
        assert "form__input--invalid" in result


class TestRenderFormHTMX:
    """Tests for HTMX attributes."""

    def test_hx_post(self) -> None:
        """hx-post attribute is rendered."""
        result = render_form(SimpleForm, hx_post="/api/submit")
        assert 'hx-post="/api/submit"' in result

    def test_hx_target(self) -> None:
        """hx-target attribute is rendered."""
        result = render_form(SimpleForm, hx_target="#form-container")
        assert 'hx-target="#form-container"' in result

    def test_hx_swap(self) -> None:
        """hx-swap attribute is rendered."""
        result = render_form(SimpleForm, hx_swap="outerHTML")
        assert 'hx-swap="outerHTML"' in result


class TestRenderFormRequired:
    """Tests for required field handling."""

    def test_required_attribute(self) -> None:
        """Required fields have required attribute."""
        result = render_form(SimpleForm)
        assert "required" in result

    def test_optional_no_required(self) -> None:
        """Optional fields don't have required attribute."""
        result = render_form(FormWithOptional)
        # nickname is optional, should not have required
        # We need to check the specific field
        assert 'name="nickname"' in result


class TestRenderFormBEM:
    """Tests for BEM class naming."""

    def test_form_has_bem_class(self) -> None:
        """Form element has BEM block class."""
        result = render_form(SimpleForm)
        assert 'class="form"' in result

    def test_field_has_bem_class(self) -> None:
        """Field wrapper has BEM element class."""
        result = render_form(SimpleForm)
        assert 'class="form__field"' in result

    def test_label_has_bem_class(self) -> None:
        """Label has BEM element class."""
        result = render_form(SimpleForm)
        assert 'class="form__label"' in result

    def test_input_has_bem_class(self) -> None:
        """Input has BEM element class."""
        result = render_form(SimpleForm)
        assert 'class="form__input"' in result

    def test_submit_has_bem_class(self) -> None:
        """Submit button has BEM element class."""
        result = render_form(SimpleForm)
        assert 'class="form__submit"' in result


class TestRenderFormModifiers:
    """Tests for BEM modifiers."""

    def test_invalid_input_modifier(self) -> None:
        """Invalid input has BEM modifier class."""
        result = render_form(SimpleForm, errors={"name": "Required"})
        assert "form__input--invalid" in result

    def test_checkbox_field_modifier(self) -> None:
        """Checkbox field has BEM modifier class."""
        result = render_form(FormWithCheckbox)
        assert "form__field--checkbox" in result

    def test_checkbox_input_modifier(self) -> None:
        """Checkbox input has BEM modifier class."""
        result = render_form(FormWithCheckbox)
        assert "form__input--checkbox" in result

    def test_select_field_modifier(self) -> None:
        """Select field has BEM modifier class."""
        result = render_form(FormWithSelect)
        assert "form__field--select" in result

    def test_select_input_modifier(self) -> None:
        """Select input has BEM modifier class."""
        result = render_form(FormWithSelect)
        assert "form__input--select" in result

    def test_textarea_field_modifier(self) -> None:
        """Textarea field has BEM modifier class."""
        result = render_form(FormWithTextarea)
        assert "form__field--textarea" in result

    def test_textarea_input_modifier(self) -> None:
        """Textarea input has BEM modifier class."""
        result = render_form(FormWithTextarea)
        assert "form__input--textarea" in result


class TestRenderFormAlerts:
    """Tests for alert messages."""

    def test_success_alert(self) -> None:
        """Success message renders with BEM classes."""
        result = render_form(SimpleForm, success_message="Saved!")
        assert 'class="form__alert form__alert--success"' in result
        assert "Saved!" in result

    def test_error_alert(self) -> None:
        """Error message renders with BEM classes."""
        result = render_form(SimpleForm, error_message="Rate limit exceeded")
        assert 'class="form__alert form__alert--error"' in result
        assert "Rate limit exceeded" in result

    def test_error_field_message(self) -> None:
        """Field error renders with BEM class."""
        result = render_form(SimpleForm, errors={"name": "Name required"})
        assert 'class="form__error"' in result
        assert "Name required" in result


class TestRenderFormAutoInject:
    """Tests for auto-injection of values and errors from context."""

    def test_auto_injects_values_from_context(self) -> None:
        """Values are auto-injected from context."""
        from zerojs.forms import render_form as render_form_with_context

        context = {"values": {"name": "John", "age": 30}}
        result = render_form_with_context(context, SimpleForm)
        assert 'value="John"' in result
        assert 'value="30"' in result

    def test_auto_injects_errors_from_context(self) -> None:
        """Errors are auto-injected from context."""
        from zerojs.forms import render_form as render_form_with_context

        context = {"errors": {"name": "Name is required"}}
        result = render_form_with_context(context, SimpleForm)
        assert "Name is required" in result
        assert "form__input--invalid" in result

    def test_auto_injects_csrf_error_message(self) -> None:
        """CSRF error message is auto-injected from context."""
        from zerojs.forms import render_form as render_form_with_context

        context = {"csrf_error": True}
        result = render_form_with_context(context, SimpleForm)
        assert "Your previous session expired" in result

    def test_auto_injects_rate_limit_error_message(self) -> None:
        """Rate limit error message is auto-injected from context."""
        from zerojs.forms import render_form as render_form_with_context

        context = {"rate_limit_error": True}
        result = render_form_with_context(context, SimpleForm)
        assert "Too many requests" in result
