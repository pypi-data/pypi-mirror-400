"""Tests for locator cache."""

import os
import tempfile
from playwright_self_healing.cache import LocatorCache


def test_cache_get_set():
    """Test cache get and set operations."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        cache_path = f.name

    try:
        cache = LocatorCache(cache_path)

        # Set a locator
        cache.set(
            "test_key",
            "page.get_by_role('button', name='Test')",
            "page.get_by_role('button', name='Original')",
            heal_count=1
        )

        # Get the locator
        result = cache.get("test_key")
        assert result == "page.get_by_role('button', name='Test')"

    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)


def test_cache_miss():
    """Test cache miss."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        cache_path = f.name

    try:
        cache = LocatorCache(cache_path)
        result = cache.get("nonexistent_key")
        assert result is None

    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)


def test_cache_clear():
    """Test cache clear."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        cache_path = f.name

    try:
        cache = LocatorCache(cache_path)

        # Add some entries
        cache.set("key1", "locator1", "original1")
        cache.set("key2", "locator2", "original2")

        # Clear cache
        cache.clear()

        # Verify cleared
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)


def test_cache_stats():
    """Test cache statistics."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        cache_path = f.name

    try:
        cache = LocatorCache(cache_path)

        # Add entries with heal counts
        cache.set("key1", "locator1", "original1", heal_count=2)
        cache.set("key2", "locator2", "original2", heal_count=3)

        # Get stats
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["total_heals"] == 5

    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)
