"""Tests for the start() method and its helper functions."""

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from zerojs import ZeroJS


@pytest.fixture(autouse=True)
def clean_dev_mode_env() -> Generator[None, None, None]:
    """Ensure ZEROJS_DEV_MODE is cleaned up after each test."""
    yield
    os.environ.pop("ZEROJS_DEV_MODE", None)


class TestStartMethod:
    """Tests for the start() method."""

    @pytest.fixture(autouse=True)
    def mock_watchfiles_installed(self) -> Generator[None, None, None]:
        """Mock watchfiles as installed to suppress warnings."""
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            yield

    def test_start_without_reload_runs_directly(self, app_dir: Path) -> None:
        """start() without reload runs uvicorn with FastAPI app directly."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run") as mock_run:
            app.start(host="0.0.0.0", port=8000, reload=False)

            mock_run.assert_called_once_with(
                app._fastapi,
                host="0.0.0.0",
                port=8000,
            )

    def test_start_with_reload_sets_dev_mode_env(self, app_dir: Path) -> None:
        """start() with reload sets ZEROJS_DEV_MODE environment variable."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run"):
            app.start(reload=True)

        assert os.environ.get("ZEROJS_DEV_MODE") == "1"

    def test_start_with_reload_uses_module_path(self, app_dir: Path) -> None:
        """start() with reload calls uvicorn with module:app string."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run") as mock_run:
            # Simulate being called from a module
            with patch("inspect.currentframe") as mock_frame:
                mock_back = MagicMock()
                mock_back.f_globals = {
                    "__name__": "mymodule",
                    "__file__": "/path/to/mymodule.py",
                    "app": app,
                }
                mock_frame.return_value.f_back = mock_back

                app.start(host="127.0.0.1", port=3000, reload=True)

                mock_run.assert_called_once_with(
                    "mymodule:app.asgi_app",
                    host="127.0.0.1",
                    port=3000,
                    reload=True,
                    reload_includes=["*.html", "*.css", "*.js", "*.py"],
                )

    def test_start_with_reload_resolves_main_module(self, app_dir: Path) -> None:
        """start() with reload resolves __main__ to actual module name."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run") as mock_run:
            with patch("inspect.currentframe") as mock_frame:
                mock_back = MagicMock()
                mock_back.f_globals = {
                    "__name__": "__main__",
                    "__file__": "/path/to/server.py",
                    "my_app": app,
                }
                mock_frame.return_value.f_back = mock_back

                app.start(reload=True)

                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == "server:my_app.asgi_app"

    def test_start_with_reload_no_frame_falls_back(self, app_dir: Path) -> None:
        """start() with reload falls back to direct run if frame unavailable."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run") as mock_run:
            with patch("inspect.currentframe", return_value=None):
                app.start(reload=True)

                mock_run.assert_called_once_with(
                    app._fastapi,
                    host="127.0.0.1",
                    port=3000,
                )

    def test_start_with_reload_no_app_var_falls_back(self, app_dir: Path) -> None:
        """start() with reload falls back if app variable not found."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("uvicorn.run") as mock_run:
            with patch("inspect.currentframe") as mock_frame:
                mock_back = MagicMock()
                # No app variable in globals
                mock_back.f_globals = {
                    "__name__": "mymodule",
                    "__file__": "/path/to/mymodule.py",
                }
                mock_frame.return_value.f_back = mock_back

                app.start(reload=True)

                mock_run.assert_called_once_with(
                    app._fastapi,
                    host="127.0.0.1",
                    port=3000,
                )


class TestWarnMissingWatchfiles:
    """Tests for _warn_missing_watchfiles helper."""

    def test_warns_when_watchfiles_not_installed(self, app_dir: Path) -> None:
        """_warn_missing_watchfiles emits warning when watchfiles is missing."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("importlib.util.find_spec", return_value=None):
            with pytest.warns(UserWarning, match="watchfiles not installed"):
                app._warn_missing_watchfiles()

    def test_no_warning_when_watchfiles_installed(self, app_dir: Path) -> None:
        """_warn_missing_watchfiles does not warn when watchfiles is installed."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        with patch("importlib.util.find_spec", return_value=MagicMock()):
            import warnings

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                app._warn_missing_watchfiles()
                assert len(w) == 0


class TestFindAppVariable:
    """Tests for _find_app_variable helper."""

    def test_finds_app_variable_by_identity(self, app_dir: Path) -> None:
        """_find_app_variable finds the variable holding the app instance."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        caller_globals: dict[str, Any] = {
            "other_var": "something",
            "my_app": app,
            "another": 123,
        }

        result = app._find_app_variable(caller_globals)
        assert result == "my_app"

    def test_returns_none_when_not_found(self, app_dir: Path) -> None:
        """_find_app_variable returns None if app not in globals."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        caller_globals: dict[str, Any] = {
            "other_var": "something",
            "another": 123,
        }

        result = app._find_app_variable(caller_globals)
        assert result is None


class TestResolveModuleName:
    """Tests for _resolve_module_name helper."""

    def test_returns_module_name_directly(self, app_dir: Path) -> None:
        """_resolve_module_name returns module name when not __main__."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        caller_globals: dict[str, Any] = {
            "__name__": "mypackage.mymodule",
            "__file__": "/path/to/mymodule.py",
        }

        result = app._resolve_module_name(caller_globals)
        assert result == "mypackage.mymodule"

    def test_resolves_main_from_file(self, app_dir: Path) -> None:
        """_resolve_module_name resolves __main__ to filename without extension."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        caller_globals: dict[str, Any] = {
            "__name__": "__main__",
            "__file__": "/path/to/my_server.py",
        }

        result = app._resolve_module_name(caller_globals)
        assert result == "my_server"

    def test_handles_missing_file(self, app_dir: Path) -> None:
        """_resolve_module_name handles missing __file__ gracefully."""
        os.chdir(app_dir)

        app = ZeroJS(
            pages_dir=app_dir / "pages",
            components_dir=app_dir / "components",
            errors_dir=app_dir / "errors",
            settings_file=app_dir / "settings.py",
        )

        caller_globals: dict[str, Any] = {
            "__name__": "__main__",
        }

        result = app._resolve_module_name(caller_globals)
        # Returns empty string when __file__ is missing
        assert result == ""
