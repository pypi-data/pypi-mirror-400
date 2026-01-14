"""HTML response cache with multiple strategies."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class CacheStrategy(str, Enum):
    """Cache strategy options."""

    NONE = "none"  # No caching
    TTL = "ttl"  # Hard expiration after TTL
    INCREMENTAL = "incremental"  # Serve stale, re-render in background


@dataclass
class CacheConfig:
    """Configuration for a cached route."""

    strategy: CacheStrategy
    ttl: int  # Seconds

    @classmethod
    def from_dict(cls, data: dict) -> "CacheConfig":
        """Create CacheConfig from a dictionary."""
        strategy = CacheStrategy(data.get("strategy", "none"))
        ttl = data.get("ttl", 0)
        return cls(strategy=strategy, ttl=ttl)

    @classmethod
    def none(cls) -> "CacheConfig":
        """Create a no-cache config."""
        return cls(strategy=CacheStrategy.NONE, ttl=0)


@dataclass
class CacheEntry:
    """A cached HTML response with timestamp."""

    html: str
    cached_at: float


@dataclass
class CacheResult:
    """Result from cache lookup."""

    html: str | None
    should_render: bool  # True if caller should render
    should_rerender_background: bool  # True if background re-render needed


class HTMLCache:
    """In-memory cache for rendered HTML pages."""

    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._rerendering: set[str] = set()  # Keys currently being re-rendered

    def get(self, key: str, config: CacheConfig) -> CacheResult:
        """Get cached HTML with render decision.

        Args:
            key: Cache key (usually the full URL path)
            config: Cache configuration for this route

        Returns:
            CacheResult with html and render decisions
        """
        # No cache strategy
        if config.strategy == CacheStrategy.NONE:
            return CacheResult(
                html=None, should_render=True, should_rerender_background=False
            )

        entry = self._cache.get(key)

        # No cached entry - need to render
        if entry is None:
            return CacheResult(
                html=None, should_render=True, should_rerender_background=False
            )

        age = time.time() - entry.cached_at

        if config.strategy == CacheStrategy.TTL:
            # TTL: hard expiration
            if age >= config.ttl:
                del self._cache[key]
                return CacheResult(
                    html=None, should_render=True, should_rerender_background=False
                )
            return CacheResult(
                html=entry.html, should_render=False, should_rerender_background=False
            )

        elif config.strategy == CacheStrategy.INCREMENTAL:
            # Incremental: always serve cached, re-render in background if stale
            is_stale = age >= config.ttl
            needs_rerender = is_stale and key not in self._rerendering
            return CacheResult(
                html=entry.html,
                should_render=False,
                should_rerender_background=needs_rerender,
            )

        # Fallback
        return CacheResult(
            html=None, should_render=True, should_rerender_background=False
        )

    def set(self, key: str, html: str) -> None:
        """Store HTML in cache."""
        self._cache[key] = CacheEntry(html=html, cached_at=time.time())
        self._rerendering.discard(key)

    def mark_rerendering(self, key: str) -> None:
        """Mark a key as currently being re-rendered."""
        self._rerendering.add(key)

    def invalidate(self, key: str) -> None:
        """Remove a specific entry from cache."""
        self._cache.pop(key, None)
        self._rerendering.discard(key)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._rerendering.clear()
