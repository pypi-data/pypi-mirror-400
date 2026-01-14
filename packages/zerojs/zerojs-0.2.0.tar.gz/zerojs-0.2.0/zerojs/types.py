"""Type annotations for ZeroJS."""

from pathlib import Path


class UnsafeStr(str):
    """String type that opts out of path traversal validation.

    Use this type hint when you explicitly need to accept path traversal
    sequences like ".." or absolute paths in URL parameters.

    Example:
        def get(query: UnsafeStr) -> dict:
            # query can contain "..", "/etc/passwd", etc.
            return {"query": query}

    Warning:
        Only use this when you understand the security implications.
        Never use UnsafeStr values directly in file system operations.
    """

    pass


class UnsafePath(Path):
    """Path type that opts out of path traversal validation.

    Use this type hint when you explicitly need to accept path traversal
    sequences like ".." or absolute paths in URL parameters.

    Example:
        def get(file: UnsafePath) -> dict:
            # file can contain "..", "/etc/passwd", etc.
            return {"file": str(file)}

    Warning:
        Only use this when you understand the security implications.
        Never use UnsafePath values directly in file system operations
        without additional validation.
    """

    pass


__all__ = ["UnsafePath", "UnsafeStr"]
