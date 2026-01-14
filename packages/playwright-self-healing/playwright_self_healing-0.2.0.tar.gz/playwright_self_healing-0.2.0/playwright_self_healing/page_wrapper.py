"""Self-healing page wrapper - main entry point for users."""

from typing import Any, Optional
from playwright.sync_api import Page, Locator
import logging

from .config import get_config
from .cache import LocatorCache
from .rate_limiter import RateLimiter
from .claude_finder import ClaudeFinder
from .screenshot_cache import ScreenshotCache
from .locator_wrapper import SelfHealingLocator


logger = logging.getLogger(__name__)


class SelfHealingPage:
    """
    Wraps a Playwright Page to provide self-healing capabilities.
    Main entry point for users of the library.
    """

    def __init__(self, page: Page, context: str = "", enable_visual_feedback: bool = True, slow_operation_threshold: float = 5.0):
        """
        Initialize self-healing page wrapper.

        Args:
            page: Playwright Page object to wrap.
            context: Optional human-readable context for the page (e.g., "Login page").
            enable_visual_feedback: Enable visual overlay during self-healing (default: True).
            slow_operation_threshold: Seconds before showing "taking longer" message (default: 5.0).

        Raises:
            ValueError: If configuration is invalid.
        """
        self._page = page
        self._context = context
        self._enable_visual_feedback = enable_visual_feedback
        self._slow_operation_threshold = slow_operation_threshold

        # Load and validate configuration
        config = get_config()
        is_valid, error_msg = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {error_msg}")

        # Initialize self-healing infrastructure
        self._cache = LocatorCache(f"{config.cache_dir}/locators.yaml")
        self._rate_limiter = RateLimiter(
            max_calls=config.max_retries,
            session_file=".temp/self_healing_session.json"
        )
        self._claude_finder = ClaudeFinder(
            api_key=config.anthropic_api_key,
            model=config.claude_model
        )
        self._screenshot_cache = ScreenshotCache(
            cache_dir=".temp/screenshots",
            ttl_seconds=config.screenshot_cache_ttl
        )

        logger.info(
            f"Initialized SelfHealingPage (context: '{context or 'default'}', "
            f"visual_feedback: {enable_visual_feedback})"
        )

    def _create_healing_locator(
        self,
        locator: Locator,
        description: str
    ) -> SelfHealingLocator:
        """
        Create a self-healing locator wrapper.

        Args:
            locator: Original Playwright Locator.
            description: Human-readable description of the element.

        Returns:
            SelfHealingLocator instance.
        """
        # Generate cache key based on page context and element description
        cache_key = f"{self._context}:{description}" if self._context else description

        return SelfHealingLocator(
            locator=locator,
            context=description,
            page=self._page,
            cache_manager=self._cache,
            rate_limiter=self._rate_limiter,
            claude_finder=self._claude_finder,
            screenshot_cache=self._screenshot_cache,
            cache_key=cache_key,
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    # Delegate Page methods that return Locators

    def get_by_role(self, role: str, **kwargs) -> SelfHealingLocator:
        """Get element by role with self-healing."""
        locator = self._page.get_by_role(role, **kwargs)
        name = kwargs.get("name", role)
        description = f"get_by_role({role}, name={name})"
        return self._create_healing_locator(locator, description)

    def get_by_label(self, text: str, **kwargs) -> SelfHealingLocator:
        """Get element by label with self-healing."""
        locator = self._page.get_by_label(text, **kwargs)
        description = f"get_by_label({text})"
        return self._create_healing_locator(locator, description)

    def get_by_text(self, text: str, **kwargs) -> SelfHealingLocator:
        """Get element by text with self-healing."""
        locator = self._page.get_by_text(text, **kwargs)
        description = f"get_by_text({text})"
        return self._create_healing_locator(locator, description)

    def get_by_placeholder(self, text: str, **kwargs) -> SelfHealingLocator:
        """Get element by placeholder with self-healing."""
        locator = self._page.get_by_placeholder(text, **kwargs)
        description = f"get_by_placeholder({text})"
        return self._create_healing_locator(locator, description)

    def get_by_alt_text(self, text: str, **kwargs) -> SelfHealingLocator:
        """Get element by alt text with self-healing."""
        locator = self._page.get_by_alt_text(text, **kwargs)
        description = f"get_by_alt_text({text})"
        return self._create_healing_locator(locator, description)

    def get_by_title(self, text: str, **kwargs) -> SelfHealingLocator:
        """Get element by title with self-healing."""
        locator = self._page.get_by_title(text, **kwargs)
        description = f"get_by_title({text})"
        return self._create_healing_locator(locator, description)

    def get_by_test_id(self, test_id: str) -> SelfHealingLocator:
        """Get element by test ID with self-healing."""
        locator = self._page.get_by_test_id(test_id)
        description = f"get_by_test_id({test_id})"
        return self._create_healing_locator(locator, description)

    def locator(self, selector: str) -> SelfHealingLocator:
        """Get element by CSS selector with self-healing."""
        locator = self._page.locator(selector)
        description = f"locator({selector})"
        return self._create_healing_locator(locator, description)

    # Delegate other Page methods (non-locator methods)

    def goto(self, url: str, **kwargs):
        """Navigate to URL."""
        return self._page.goto(url, **kwargs)

    def reload(self, **kwargs):
        """Reload the page."""
        return self._page.reload(**kwargs)

    def go_back(self, **kwargs):
        """Go back in history."""
        return self._page.go_back(**kwargs)

    def go_forward(self, **kwargs):
        """Go forward in history."""
        return self._page.go_forward(**kwargs)

    def wait_for_load_state(self, state: Optional[str] = None, **kwargs):
        """Wait for load state."""
        return self._page.wait_for_load_state(state, **kwargs)

    def wait_for_timeout(self, timeout: float):
        """Wait for specified timeout."""
        return self._page.wait_for_timeout(timeout)

    def wait_for_url(self, url, **kwargs):
        """Wait for URL."""
        return self._page.wait_for_url(url, **kwargs)

    def title(self) -> str:
        """Get page title."""
        return self._page.title()

    @property
    def url(self) -> str:
        """Get current URL."""
        return self._page.url

    def content(self) -> str:
        """Get page HTML content."""
        return self._page.content()

    def screenshot(self, **kwargs) -> bytes:
        """Take a screenshot."""
        return self._page.screenshot(**kwargs)

    def close(self, **kwargs):
        """Close the page."""
        return self._page.close(**kwargs)

    def set_viewport_size(self, viewport_size: dict):
        """Set viewport size."""
        return self._page.set_viewport_size(viewport_size)

    @property
    def viewport_size(self) -> Optional[dict]:
        """Get viewport size."""
        return self._page.viewport_size

    def evaluate(self, expression: str, arg: Any = None) -> Any:
        """Evaluate JavaScript expression."""
        return self._page.evaluate(expression, arg)

    def add_script_tag(self, **kwargs):
        """Add script tag to page."""
        return self._page.add_script_tag(**kwargs)

    def add_style_tag(self, **kwargs):
        """Add style tag to page."""
        return self._page.add_style_tag(**kwargs)

    # Expose underlying page for advanced usage
    @property
    def page(self) -> Page:
        """Get the underlying Playwright Page object."""
        return self._page

    # Statistics and debugging
    def get_healing_stats(self) -> dict:
        """
        Get statistics about self-healing operations.

        Returns:
            Dictionary with cache, rate limiter, and screenshot cache stats.
        """
        return {
            "cache": self._cache.get_stats(),
            "rate_limiter": self._rate_limiter.get_stats(),
            "screenshot_cache": self._screenshot_cache.get_stats()
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"SelfHealingPage(url='{self.url}', context='{self._context}')"
