"""Client-side counter logic using PyScript/MicroPython."""

from pyscript import document, when


@when("click", "#btn-increment")
def increment(event):
    """Increment the counter."""
    el = document.querySelector("#count")
    el.innerText = str(int(el.innerText) + 1)


@when("click", "#btn-decrement")
def decrement(event):
    """Decrement the counter."""
    el = document.querySelector("#count")
    el.innerText = str(int(el.innerText) - 1)
