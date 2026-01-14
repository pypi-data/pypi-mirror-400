"""Screenshot caching to avoid repeated captures."""

import os
import hashlib
import threading
from datetime import datetime
from typing import Dict, Tuple
from playwright.sync_api import Page
import logging


logger = logging.getLogger(__name__)


class ScreenshotCache:
    """
    Caches screenshots for a short duration to avoid repeated captures.
    """

    def __init__(self, cache_dir: str = ".temp/screenshots", ttl_seconds: int = 30):
        """
        Initialize the screenshot cache.

        Args:
            cache_dir: Directory to store screenshot files.
            ttl_seconds: Time-to-live for cached screenshots in seconds.
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[str, datetime]] = {}  # {cache_key: (screenshot_path, timestamp)}
        self.lock = threading.Lock()
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_or_capture(self, page: Page) -> str:
        """
        Return a screenshot path, either from cache or by capturing new.

        Args:
            page: Playwright Page object.

        Returns:
            Path to screenshot file.
        """
        with self.lock:
            cache_key = self._get_cache_key(page)

            # Check if cached and not expired
            if cache_key in self.cache:
                screenshot_path, timestamp = self.cache[cache_key]
                age = (datetime.utcnow() - timestamp).total_seconds()

                if age < self.ttl_seconds and os.path.exists(screenshot_path):
                    logger.debug(f"Screenshot cache hit (age: {age:.1f}s)")
                    return screenshot_path
                else:
                    logger.debug(f"Screenshot cache expired (age: {age:.1f}s)")

            # Capture new screenshot
            screenshot_path = self._capture_screenshot(page, cache_key)
            self.cache[cache_key] = (screenshot_path, datetime.utcnow())

            return screenshot_path

    def _get_cache_key(self, page: Page) -> str:
        """
        Generate a cache key based on page URL and viewport.

        Args:
            page: Playwright Page object.

        Returns:
            Cache key string.
        """
        url = page.url
        viewport = page.viewport_size
        viewport_str = f"{viewport['width']}x{viewport['height']}" if viewport else "default"
        key_str = f"{url}:{viewport_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _capture_screenshot(self, page: Page, cache_key: str) -> str:
        """
        Capture a screenshot and save it to disk.
        Resizes if dimensions exceed Claude's 8000px limit.

        Args:
            page: Playwright Page object.
            cache_key: Cache key for filename.

        Returns:
            Path to screenshot file.
        """
        screenshot_path = os.path.join(self.cache_dir, f"{cache_key}.png")
        try:
            # Capture viewport only (not full page) to avoid huge screenshots
            page.screenshot(path=screenshot_path, full_page=False)

            # Check and resize if needed
            self._resize_if_needed(screenshot_path)

            logger.debug(f"Screenshot captured: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
        return screenshot_path

    def _resize_if_needed(self, image_path: str, max_dimension: int = 8000):
        """
        Resize image if either dimension exceeds max_dimension.

        Args:
            image_path: Path to the image file.
            max_dimension: Maximum allowed dimension in pixels.
        """
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                width, height = img.size

                # Check if resize is needed
                if width <= max_dimension and height <= max_dimension:
                    return

                # Calculate new dimensions maintaining aspect ratio
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))

                # Resize and save
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized.save(image_path, 'PNG', optimize=True)
                logger.info(f"Resized screenshot from {width}x{height} to {new_width}x{new_height}")

        except ImportError:
            logger.warning("PIL/Pillow not installed, skipping image resize")
        except Exception as e:
            logger.warning(f"Failed to resize image: {e}")

    def cleanup_expired(self):
        """Remove expired screenshots from cache and disk."""
        with self.lock:
            now = datetime.utcnow()
            expired_keys = []

            for key, (path, timestamp) in self.cache.items():
                age = (now - timestamp).total_seconds()
                if age >= self.ttl_seconds:
                    expired_keys.append(key)
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                            logger.debug(f"Removed expired screenshot: {path}")
                        except Exception as e:
                            logger.error(f"Failed to remove screenshot {path}: {e}")

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired screenshots")

    def clear(self):
        """Clear all cached screenshots."""
        with self.lock:
            for _, (path, _) in self.cache.items():
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        logger.error(f"Failed to remove screenshot {path}: {e}")

            self.cache.clear()
            logger.info("Screenshot cache cleared")

    def get_stats(self) -> Dict[str, any]:
        """
        Get screenshot cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        with self.lock:
            return {
                "cached_screenshots": len(self.cache),
                "ttl_seconds": self.ttl_seconds
            }
