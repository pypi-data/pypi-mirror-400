"""Route registration modules."""

from .components import register_component_routes
from .pages import register_page_routes

__all__ = ["register_page_routes", "register_component_routes"]
