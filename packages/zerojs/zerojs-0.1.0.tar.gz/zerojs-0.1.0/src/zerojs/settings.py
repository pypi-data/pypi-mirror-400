"""Settings loader for user configuration."""

import importlib.util
from pathlib import Path
from typing import Any

from .cache import CacheConfig, CacheStrategy


def load_user_settings(settings_file: Path | None = None) -> dict[str, Any]:
    """Load settings from user's settings.py file.

    Args:
        settings_file: Path to settings.py. If None, looks in current directory.

    Returns:
        Dictionary with settings. Defaults are used for missing values.
    """
    defaults: dict[str, Any] = {
        # Cache settings
        "CACHE_STRATEGY": "none",  # "none" | "ttl" | "incremental"
        "CACHE_TTL": 0,  # Default TTL in seconds
        "CACHE_ROUTES": {},  # Per-route overrides: {"/path": {"strategy": "...", "ttl": N}}
        # PyScript settings
        "PYSCRIPT_ENABLED": False,
        "PYSCRIPT_RUNTIME": "micropython",  # "micropython" | "pyodide"
        "PYSCRIPT_VERSION": "2025.10.1",
    }

    if settings_file is None:
        settings_file = Path("settings.py")

    if not settings_file.exists():
        return defaults

    try:
        spec = importlib.util.spec_from_file_location("settings", settings_file)
        if spec is None or spec.loader is None:
            return defaults

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract known settings
        result = defaults.copy()
        for key in defaults:
            if hasattr(module, key):
                result[key] = getattr(module, key)

        return result

    except Exception:
        return defaults


def get_cache_config(settings: dict[str, Any], url_path: str) -> CacheConfig:
    """Get cache configuration for a specific URL path.

    Args:
        settings: Loaded settings dictionary
        url_path: The URL path (e.g., "/users/1")

    Returns:
        CacheConfig for this route
    """
    cache_routes: dict[str, dict[str, Any]] = settings.get("CACHE_ROUTES", {})

    # Check for exact route match
    if url_path in cache_routes:
        route_config = cache_routes[url_path]
        return CacheConfig.from_dict(route_config)

    # Use global defaults
    strategy_str = settings.get("CACHE_STRATEGY", "none")
    try:
        strategy = CacheStrategy(strategy_str)
    except ValueError:
        strategy = CacheStrategy.NONE

    ttl = settings.get("CACHE_TTL", 0)

    # If strategy is none or ttl is 0, return no-cache config
    if strategy == CacheStrategy.NONE or (strategy != CacheStrategy.NONE and ttl <= 0):
        return CacheConfig.none()

    return CacheConfig(strategy=strategy, ttl=ttl)
