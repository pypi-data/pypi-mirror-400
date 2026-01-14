"""Tests for HTML caching."""

import time
from pathlib import Path

from fastapi.testclient import TestClient

from zerojs import ZeroJS
from zerojs.cache import CacheConfig, CacheStrategy, HTMLCache


class TestHTMLCache:
    """Tests for the HTMLCache class."""

    def test_get_with_none_strategy_always_returns_should_render(self) -> None:
        """Cache with NONE strategy always requires rendering."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")
        config = CacheConfig(strategy=CacheStrategy.NONE, ttl=60)
        result = cache.get("/test", config)
        assert result.html is None
        assert result.should_render is True
        assert result.should_rerender_background is False

    def test_get_returns_should_render_when_empty(self) -> None:
        """Cache returns should_render=True for missing keys."""
        cache = HTMLCache()
        config = CacheConfig(strategy=CacheStrategy.TTL, ttl=60)
        result = cache.get("/test", config)
        assert result.html is None
        assert result.should_render is True

    def test_set_and_get_with_ttl_strategy(self) -> None:
        """Cache stores and retrieves HTML with TTL strategy."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")
        config = CacheConfig(strategy=CacheStrategy.TTL, ttl=60)
        result = cache.get("/test", config)
        assert result.html == "<html>Test</html>"
        assert result.should_render is False

    def test_cache_expires_with_ttl_strategy(self) -> None:
        """Cache entry expires after TTL with TTL strategy."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")

        # Should return cached value with long TTL
        config = CacheConfig(strategy=CacheStrategy.TTL, ttl=60)
        result = cache.get("/test", config)
        assert result.html == "<html>Test</html>"
        assert result.should_render is False

        # Wait and check with very short TTL
        time.sleep(0.1)
        config_short = CacheConfig(strategy=CacheStrategy.TTL, ttl=0.05)
        result = cache.get("/test", config_short)
        assert result.html is None
        assert result.should_render is True

    def test_incremental_strategy_serves_stale_and_triggers_rerender(self) -> None:
        """Incremental strategy serves stale content and triggers background re-render."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")

        # Should return cached value immediately
        config = CacheConfig(strategy=CacheStrategy.INCREMENTAL, ttl=60)
        result = cache.get("/test", config)
        assert result.html == "<html>Test</html>"
        assert result.should_render is False
        assert result.should_rerender_background is False

        # Wait past TTL
        time.sleep(0.1)
        config_short = CacheConfig(strategy=CacheStrategy.INCREMENTAL, ttl=0.05)
        result = cache.get("/test", config_short)
        assert result.html == "<html>Test</html>"  # Still serves stale
        assert result.should_render is False
        assert result.should_rerender_background is True  # Needs background re-render

    def test_incremental_strategy_no_rerender_if_already_rerendering(self) -> None:
        """Incremental strategy doesn't trigger re-render if already in progress."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")
        cache.mark_rerendering("/test")

        time.sleep(0.1)
        config = CacheConfig(strategy=CacheStrategy.INCREMENTAL, ttl=0.05)
        result = cache.get("/test", config)
        assert result.html == "<html>Test</html>"
        assert result.should_rerender_background is False  # Already rerendering

    def test_invalidate(self) -> None:
        """Cache entry can be invalidated."""
        cache = HTMLCache()
        cache.set("/test", "<html>Test</html>")
        config = CacheConfig(strategy=CacheStrategy.TTL, ttl=60)

        result = cache.get("/test", config)
        assert result.html == "<html>Test</html>"

        cache.invalidate("/test")
        result = cache.get("/test", config)
        assert result.html is None
        assert result.should_render is True

    def test_invalidate_nonexistent(self) -> None:
        """Invalidating nonexistent key doesn't raise."""
        cache = HTMLCache()
        cache.invalidate("/nonexistent")  # Should not raise

    def test_clear(self) -> None:
        """Cache can be cleared entirely."""
        cache = HTMLCache()
        cache.set("/a", "<html>A</html>")
        cache.set("/b", "<html>B</html>")

        cache.clear()

        config = CacheConfig(strategy=CacheStrategy.TTL, ttl=60)
        assert cache.get("/a", config).html is None
        assert cache.get("/b", config).html is None


class TestCacheConfig:
    """Tests for CacheConfig class."""

    def test_from_dict_with_strategy_and_ttl(self) -> None:
        """CacheConfig.from_dict parses strategy and ttl."""
        config = CacheConfig.from_dict({"strategy": "ttl", "ttl": 120})
        assert config.strategy == CacheStrategy.TTL
        assert config.ttl == 120

    def test_from_dict_defaults(self) -> None:
        """CacheConfig.from_dict uses defaults for missing values."""
        config = CacheConfig.from_dict({})
        assert config.strategy == CacheStrategy.NONE
        assert config.ttl == 0

    def test_none_factory(self) -> None:
        """CacheConfig.none() creates no-cache config."""
        config = CacheConfig.none()
        assert config.strategy == CacheStrategy.NONE
        assert config.ttl == 0


class TestAppCacheIntegration:
    """Integration tests for app-level caching."""

    def test_no_cache_by_default(self, tmp_path: Path) -> None:
        """Without settings.py, cache is disabled."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        # Create a page that shows current time
        (pages_dir / "time.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_time.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        import os

        os.chdir(tmp_path)

        app = ZeroJS(pages_dir=pages_dir, components_dir=components_dir)
        client = TestClient(app.asgi_app)

        # Two requests should return different timestamps
        response1 = client.get("/time")
        time.sleep(0.01)
        response2 = client.get("/time")

        assert response1.text != response2.text

    def test_cache_with_ttl_strategy(self, tmp_path: Path) -> None:
        """With CACHE_STRATEGY=ttl in settings.py, responses are cached."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        # Create settings.py with TTL cache enabled
        (tmp_path / "settings.py").write_text("""
CACHE_STRATEGY = "ttl"
CACHE_TTL = 60
""")

        # Create a page that shows current time
        (pages_dir / "time.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_time.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        import os

        os.chdir(tmp_path)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            settings_file=tmp_path / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # Two requests should return same cached response
        response1 = client.get("/time")
        time.sleep(0.01)
        response2 = client.get("/time")

        assert response1.text == response2.text

    def test_cache_routes_override(self, tmp_path: Path) -> None:
        """CACHE_ROUTES can override strategy per route."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        # Create settings with route-specific config
        (tmp_path / "settings.py").write_text("""
CACHE_STRATEGY = "none"  # Default: no cache
CACHE_TTL = 0
CACHE_ROUTES = {
    "/cached": {"strategy": "ttl", "ttl": 60},  # This route is cached
}
""")

        # Create two pages
        (pages_dir / "cached.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_cached.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        (pages_dir / "nocache.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_nocache.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        import os

        os.chdir(tmp_path)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            settings_file=tmp_path / "settings.py",
        )
        client = TestClient(app.asgi_app)

        # /cached should return same response
        cached1 = client.get("/cached")
        time.sleep(0.01)
        cached2 = client.get("/cached")
        assert cached1.text == cached2.text

        # /nocache should return different response
        nocache1 = client.get("/nocache")
        time.sleep(0.01)
        nocache2 = client.get("/nocache")
        assert nocache1.text != nocache2.text

    def test_clear_cache(self, tmp_path: Path) -> None:
        """App.clear_cache() clears all cached responses."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (tmp_path / "settings.py").write_text("""
CACHE_STRATEGY = "ttl"
CACHE_TTL = 60
""")

        (pages_dir / "time.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_time.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        import os

        os.chdir(tmp_path)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            settings_file=tmp_path / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response1 = client.get("/time")
        app.clear_cache()
        time.sleep(0.01)
        response2 = client.get("/time")

        assert response1.text != response2.text

    def test_invalidate_cache(self, tmp_path: Path) -> None:
        """App.invalidate_cache() clears specific URL."""
        pages_dir = tmp_path / "pages"
        components_dir = tmp_path / "components"
        pages_dir.mkdir()
        components_dir.mkdir()

        (tmp_path / "settings.py").write_text("""
CACHE_STRATEGY = "ttl"
CACHE_TTL = 60
""")

        (pages_dir / "time.html").write_text("<p>{{ timestamp }}</p>")
        (pages_dir / "_time.py").write_text("""
import time
def get() -> dict:
    return {"timestamp": time.time()}
""")

        import os

        os.chdir(tmp_path)

        app = ZeroJS(
            pages_dir=pages_dir,
            components_dir=components_dir,
            settings_file=tmp_path / "settings.py",
        )
        client = TestClient(app.asgi_app)

        response1 = client.get("/time")
        app.invalidate_cache("/time")
        time.sleep(0.01)
        response2 = client.get("/time")

        assert response1.text != response2.text
