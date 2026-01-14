"""Tests for check_file_length script."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "check_file_length.py"


@pytest.fixture
def short_file(tmp_path: Path) -> Path:
    """Create a file under the limit."""
    f = tmp_path / "short.py"
    f.write_text("# line\n" * 100)
    return f


@pytest.fixture
def long_file(tmp_path: Path) -> Path:
    """Create a file over the limit."""
    f = tmp_path / "long.py"
    f.write_text("# line\n" * 1001)
    return f


@pytest.fixture
def exact_limit_file(tmp_path: Path) -> Path:
    """Create a file exactly at the limit."""
    f = tmp_path / "exact.py"
    f.write_text("# line\n" * 1000)
    return f


class TestCheckFileLength:
    """Tests for check_file_length.py script."""

    def test_short_file_passes(self, short_file: Path) -> None:
        """Files under the limit should pass."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, str(short_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_long_file_fails(self, long_file: Path) -> None:
        """Files over the limit should fail."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, str(long_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "1001 lines" in result.stdout
        assert "max 1000" in result.stdout

    def test_exact_limit_passes(self, exact_limit_file: Path) -> None:
        """Files exactly at the limit should pass."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, str(exact_limit_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_multiple_files_one_fails(self, short_file: Path, long_file: Path) -> None:
        """If any file fails, the script should fail."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, str(short_file), str(long_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert str(long_file) in result.stdout
        assert str(short_file) not in result.stdout

    def test_multiple_files_all_pass(self, short_file: Path, exact_limit_file: Path) -> None:
        """If all files pass, the script should pass."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, str(short_file), str(exact_limit_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_no_files_passes(self) -> None:
        """Running with no files should pass."""
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
