"""
Path Traversal Protection
"""

import os
from pathlib import Path, PurePath

PathLike = str | Path

_WINDOWS_RESERVED_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
)


def is_safe_path(base_directory: PathLike, user_path: PathLike) -> bool:
    """
    Validates whether a user-supplied path is safe and strictly contained
    within the allowed base directory.

    Note:
        Subject to TOCTOU race conditions. For maximum security,
        combine with OS-level sandboxing.
    """
    try:
        user_path_str = str(user_path)

        # Null bytes pueden truncar paths en syscalls
        if "\x00" in user_path_str:
            return False

        # Paths vacíos resuelven a CWD
        if not user_path_str or user_path_str.isspace():
            return False

        base_dir = Path(base_directory).resolve()

        if not base_dir.is_dir():
            return False

        candidate = PurePath(user_path_str)

        if candidate.is_absolute():
            return False

        if user_path_str.startswith("~"):
            return False

        if ".." in candidate.parts:
            return False

        # Windows reserved names (portabilidad)
        for part in candidate.parts:
            if part.split(".")[0].upper() in _WINDOWS_RESERVED_NAMES:
                return False

        # Verificación de contención (única y suficiente)
        resolved = (base_dir / candidate).resolve(strict=False)
        resolved.relative_to(base_dir)

        return True

    except (ValueError, RuntimeError, OSError, TypeError):
        return False


def secure_open_for_write(
    base_directory: PathLike,
    user_path: PathLike,
    *,
    mode: int = 0o600,
) -> int:
    """
    Safely creates a new file for writing inside base_directory.

    Guarantees:
    - Path traversal protection
    - No symlink following on final component (O_NOFOLLOW)
    - No overwrite of existing files (O_EXCL)
    - Atomic creation (TOCTOU-safe for the file itself)
    - Close-on-exec (O_CLOEXEC where available)

    Platform:
        POSIX only.

    Note:
        O_NOFOLLOW only applies to the final path component.
        For full symlink protection, use OS-level sandboxing.

    Returns:
        File descriptor (int)

    Raises:
        ValueError: Invalid or unsafe path
        FileExistsError: File already exists
        OSError: OS-level failure
    """
    if not is_safe_path(base_directory, user_path):
        raise ValueError("Unsafe path")

    base_dir = Path(base_directory).resolve()
    target = base_dir / Path(user_path)

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)

    return os.open(target, flags, mode)


def is_safe_path_segment(path_str: str) -> bool:
    """
    Validates whether a path string is safe for use as a URL path parameter.

    This is a simpler version of is_safe_path() that doesn't require a base
    directory. Use this for validating URL path parameters before converting
    them to Path objects.

    Returns False if the path contains:
    - Null bytes
    - Empty or whitespace-only strings
    - Absolute paths
    - Home directory expansion (~)
    - Parent directory references (..)
    - Windows reserved names

    Args:
        path_str: The path string to validate.

    Returns:
        True if safe, False if potentially malicious.
    """
    try:
        # Null bytes can truncate paths in syscalls
        if "\x00" in path_str:
            return False

        # Empty paths are not valid
        if not path_str or path_str.isspace():
            return False

        candidate = PurePath(path_str)

        # Reject absolute paths
        if candidate.is_absolute():
            return False

        # Reject home directory expansion
        if path_str.startswith("~"):
            return False

        # Reject parent directory traversal
        if ".." in candidate.parts:
            return False

        # Windows reserved names (for portability)
        for part in candidate.parts:
            if part.split(".")[0].upper() in _WINDOWS_RESERVED_NAMES:
                return False

        return True

    except (ValueError, RuntimeError, OSError, TypeError):
        return False


__all__ = [
    "is_safe_path",
    "is_safe_path_segment",
    "secure_open_for_write",
]
