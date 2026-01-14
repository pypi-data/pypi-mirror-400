"""File-based routing utilities."""

import re
from dataclasses import dataclass
from pathlib import Path


# File extensions that are rendered as templates
TEMPLATE_EXTENSIONS = {".html"}
# File extensions served as plain text (no templating)
STATIC_TEXT_EXTENSIONS = {".txt", ".md"}
# All supported extensions
SUPPORTED_EXTENSIONS = TEMPLATE_EXTENSIONS | STATIC_TEXT_EXTENSIONS


@dataclass
class Route:
    """Represents a route derived from a file path."""

    file_path: Path
    url_path: str
    params: list[str]
    context_file: Path | None = None
    is_static: bool = False  # True for .txt, .md files (no templating)


def _find_context_file(html_file: Path) -> Path | None:
    """Find the context file for an HTML file.

    Examples:
        [id].html -> _id.py
        index.html -> _index.py
        about.html -> _about.py
    """
    html_name = html_file.stem  # e.g., "[id]" or "index"

    # Convert [param] to _param
    if html_name.startswith("[") and html_name.endswith("]"):
        py_name = f"_{html_name[1:-1]}.py"
    else:
        py_name = f"_{html_name}.py"

    context_file = html_file.parent / py_name
    return context_file if context_file.exists() else None


def file_to_route(file_path: Path, pages_dir: Path) -> Route:
    """Convert a file path to a Route.

    Examples:
        pages/index.html -> /
        pages/about.html -> /about
        pages/users/index.html -> /users
        pages/users/[id].html -> /users/{id}
        pages/robots.txt -> /robots.txt
    """
    relative = file_path.relative_to(pages_dir)
    parts = list(relative.parts)
    extension = file_path.suffix
    is_static = extension in STATIC_TEXT_EXTENSIONS

    # For static files (.txt, .md), keep the extension in the URL
    if is_static:
        # No special handling for index, keep filename as-is
        converted_parts = list(parts)
        url_path = "/" + "/".join(converted_parts)
        return Route(
            file_path=file_path,
            url_path=url_path,
            params=[],
            context_file=None,
            is_static=True,
        )

    # Remove extension from last part (for .html)
    parts[-1] = file_path.stem

    # Handle index files
    if parts[-1] == "index":
        parts.pop()

    # Convert [param] to {param} and collect params
    params: list[str] = []
    converted_parts: list[str] = []

    for part in parts:
        match = re.match(r"^\[(\w+)\]$", part)
        if match:
            param_name = match.group(1)
            params.append(param_name)
            converted_parts.append(f"{{{param_name}}}")
        else:
            converted_parts.append(part)

    url_path = "/" + "/".join(converted_parts) if converted_parts else "/"

    # Check for context file (only for templates)
    context_file = _find_context_file(file_path)

    return Route(file_path=file_path, url_path=url_path, params=params, context_file=context_file)


def scan_pages(pages_dir: Path) -> list[Route]:
    """Scan a directory for page files and return routes."""
    if not pages_dir.exists():
        return []

    routes: list[Route] = []

    for file_path in pages_dir.rglob("*"):
        if file_path.suffix in SUPPORTED_EXTENSIONS:
            route = file_to_route(file_path, pages_dir)
            routes.append(route)

    # Sort routes: static routes first, then dynamic routes
    # This ensures /users matches before /users/{id}
    routes.sort(key=lambda r: (len(r.params), r.url_path))

    return routes
