"""Tests for path traversal protection."""

from zerojs.security.path_travesal_protection import is_safe_path_segment


class TestIsSafePathSegment:
    """Tests for is_safe_path_segment function."""

    def test_safe_simple_filename(self) -> None:
        """Simple filenames are safe."""
        assert is_safe_path_segment("file.txt") is True
        assert is_safe_path_segment("document.pdf") is True
        assert is_safe_path_segment("image.png") is True

    def test_safe_nested_path(self) -> None:
        """Nested paths without traversal are safe."""
        assert is_safe_path_segment("docs/file.txt") is True
        assert is_safe_path_segment("a/b/c/file.txt") is True
        assert is_safe_path_segment("users/123/profile.json") is True

    def test_unsafe_parent_traversal(self) -> None:
        """Parent directory traversal is rejected."""
        assert is_safe_path_segment("../file.txt") is False
        assert is_safe_path_segment("docs/../secret.txt") is False
        assert is_safe_path_segment("a/b/../../etc/passwd") is False
        assert is_safe_path_segment("..") is False

    def test_unsafe_absolute_path(self) -> None:
        """Absolute paths are rejected."""
        assert is_safe_path_segment("/etc/passwd") is False
        assert is_safe_path_segment("/home/user/file.txt") is False
        assert is_safe_path_segment("/") is False

    def test_unsafe_null_byte(self) -> None:
        """Null bytes are rejected."""
        assert is_safe_path_segment("file.txt\x00.jpg") is False
        assert is_safe_path_segment("\x00") is False

    def test_unsafe_empty_string(self) -> None:
        """Empty strings are rejected."""
        assert is_safe_path_segment("") is False
        assert is_safe_path_segment("   ") is False

    def test_unsafe_home_expansion(self) -> None:
        """Home directory expansion is rejected."""
        assert is_safe_path_segment("~") is False
        assert is_safe_path_segment("~/file.txt") is False
        assert is_safe_path_segment("~user/file.txt") is False

    def test_safe_dotfile(self) -> None:
        """Dotfiles (single dot prefix) are safe."""
        assert is_safe_path_segment(".gitignore") is True
        assert is_safe_path_segment("docs/.hidden") is True

    def test_safe_current_dir_prefix(self) -> None:
        """Current directory prefix is safe."""
        assert is_safe_path_segment("./file.txt") is True
        assert is_safe_path_segment("./docs/file.txt") is True

    def test_unsafe_windows_reserved_names(self) -> None:
        """Windows reserved names are rejected for portability."""
        assert is_safe_path_segment("CON") is False
        assert is_safe_path_segment("con") is False
        assert is_safe_path_segment("PRN") is False
        assert is_safe_path_segment("AUX") is False
        assert is_safe_path_segment("NUL") is False
        assert is_safe_path_segment("COM1") is False
        assert is_safe_path_segment("LPT1") is False
        assert is_safe_path_segment("CON.txt") is False
        assert is_safe_path_segment("docs/CON") is False
