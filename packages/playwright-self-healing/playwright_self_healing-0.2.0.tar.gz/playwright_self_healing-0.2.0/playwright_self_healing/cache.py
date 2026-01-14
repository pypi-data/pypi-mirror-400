"""YAML cache management for healed locators."""

import os
import threading
import yaml
from datetime import datetime
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


class LocatorCache:
    """
    Manages YAML cache of working locators.
    Thread-safe for parallel test execution.
    """

    def __init__(self, cache_path: str = ".cache/locators.yaml"):
        """
        Initialize the locator cache.

        Args:
            cache_path: Path to the YAML cache file.
        """
        self.cache_path = cache_path
        self.lock = threading.Lock()
        self._ensure_cache_exists()

    def _ensure_cache_exists(self):
        """Create cache directory and file if they don't exist."""
        cache_dir = os.path.dirname(self.cache_path)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        if not os.path.exists(self.cache_path):
            with open(self.cache_path, 'w') as f:
                yaml.dump({}, f)

    def get(self, cache_key: str) -> Optional[str]:
        """
        Retrieve a cached locator string.

        Args:
            cache_key: Unique identifier for the locator.

        Returns:
            Locator string if found, None otherwise.
        """
        with self.lock:
            data = self._load_cache()
            entry = data.get(cache_key)
            if entry:
                logger.debug(f"Cache hit for key: {cache_key}")
                return entry.get("locator")
            logger.debug(f"Cache miss for key: {cache_key}")
            return None

    def set(
        self,
        cache_key: str,
        locator: str,
        original_locator: str,
        heal_count: int = 0
    ):
        """
        Save a working locator to the cache.

        Args:
            cache_key: Unique identifier for the locator.
            locator: Working locator string.
            original_locator: Original locator that failed.
            heal_count: Number of times this locator was healed.
        """
        with self.lock:
            data = self._load_cache()
            data[cache_key] = {
                "locator": locator,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "original_locator": original_locator,
                "heal_count": heal_count
            }
            self._save_cache(data)
            logger.info(f"Cached healed locator for key: {cache_key}")

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache data from YAML file."""
        if not os.path.exists(self.cache_path):
            return {}

        try:
            with open(self.cache_path, 'r') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return {}

    def _save_cache(self, data: Dict[str, Any]):
        """Save cache data to YAML file."""
        try:
            with open(self.cache_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def clear(self):
        """Clear all cached locators."""
        with self.lock:
            self._save_cache({})
            logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (total entries, heal counts, etc.).
        """
        with self.lock:
            data = self._load_cache()
            total_entries = len(data)
            total_heals = sum(entry.get("heal_count", 0) for entry in data.values())

            return {
                "total_entries": total_entries,
                "total_heals": total_heals
            }
