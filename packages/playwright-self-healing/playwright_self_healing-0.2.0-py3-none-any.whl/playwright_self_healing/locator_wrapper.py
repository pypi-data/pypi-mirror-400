"""Self-healing locator wrapper that intercepts failures."""

from typing import Any, Callable, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
import logging

from .cache import LocatorCache
from .rate_limiter import RateLimiter
from .claude_finder import ClaudeFinder
from .screenshot_cache import ScreenshotCache
from .visual_feedback import get_visual_feedback, FeedbackStage


logger = logging.getLogger(__name__)


class SelfHealingLocator:
    """
    Wraps a Playwright Locator and adds self-healing capabilities.
    Delegates all operations to the underlying locator, catching failures.
    """

    def __init__(
        self,
        locator: Locator,
        context: str,
        page: Page,
        cache_manager: LocatorCache,
        rate_limiter: RateLimiter,
        claude_finder: ClaudeFinder,
        screenshot_cache: ScreenshotCache,
        cache_key: str,
        enable_visual_feedback: bool = True,
        slow_operation_threshold: float = 5.0
    ):
        """
        Initialize self-healing locator wrapper.

        Args:
            locator: Original Playwright Locator.
            context: Human-readable description of the element.
            page: Playwright Page object.
            cache_manager: Locator cache instance.
            rate_limiter: Rate limiter instance.
            claude_finder: Claude API finder instance.
            screenshot_cache: Screenshot cache instance.
            cache_key: Unique cache key for this locator.
            enable_visual_feedback: Enable visual overlay during healing (default: True).
            slow_operation_threshold: Seconds before showing "taking longer" message (default: 5.0).
        """
        self._locator = locator
        self._context = context
        self._page = page
        self._cache = cache_manager
        self._rate_limiter = rate_limiter
        self._claude_finder = claude_finder
        self._screenshot_cache = screenshot_cache
        self._cache_key = cache_key
        self._original_locator_str = str(locator)
        self._enable_visual_feedback = enable_visual_feedback
        self._slow_operation_threshold = slow_operation_threshold

    @property
    def _impl_obj(self):
        """
        Expose the underlying Playwright implementation object.
        This is required for compatibility with Playwright's expect() and other internal APIs.
        """
        return self._locator._impl_obj

    def __getattr__(self, name: str):
        """
        Delegate unknown attributes to the underlying Playwright Locator.
        This ensures compatibility with Playwright's internal APIs and any methods we haven't explicitly wrapped.
        """
        # Avoid infinite recursion by checking if we're trying to access our own internal attributes
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        # Delegate to the underlying locator
        attr = getattr(self._locator, name)

        # If it's a callable method, we could wrap it with healing, but for simplicity
        # and to avoid breaking Playwright's internal behavior, just return it as-is
        return attr

    def _execute_with_healing(self, method_name: str, *args, **kwargs) -> Any:
        """
        Core wrapper method that handles self-healing.

        Args:
            method_name: Name of the locator method to execute.
            *args: Arguments for the operation.
            **kwargs: Keyword arguments for the operation.

        Returns:
            Result of the operation.

        Raises:
            Original exception if healing fails or is not possible.
        """
        feedback = get_visual_feedback() if self._enable_visual_feedback else None

        # Check cache FIRST - if we have a healed locator, use it immediately
        cached_locator_str = self._cache.get(self._cache_key)
        if cached_locator_str:
            logger.debug(f"Found cached healed locator for '{self._context}': {cached_locator_str}")
            try:
                cached_locator = self._claude_finder.locator_string_to_playwright(
                    self._page, cached_locator_str
                )
                if cached_locator:
                    # Use the cached locator directly
                    self._locator = cached_locator
                    method = getattr(self._locator, method_name)
                    return method(*args, **kwargs)
            except Exception as cache_error:
                logger.warning(f"Cached locator failed, trying original: {cache_error}")
                # Fall through to try original locator

        try:
            # Start browser-side timer for slow operation detection
            if feedback and self._slow_operation_threshold > 0:
                threshold_ms = int(self._slow_operation_threshold * 1000)
                feedback.start_slow_timer(self._page, threshold_ms)

            # Try original locator
            method = getattr(self._locator, method_name)
            result = method(*args, **kwargs)

            # Operation succeeded - cancel timer and hide any feedback shown
            if feedback:
                feedback.cancel_slow_timer(self._page)
                # Hide overlay if slow feedback was shown
                feedback.hide(self._page)

            return result

        except (PlaywrightTimeoutError, Exception) as e:
            logger.warning(f"Locator failed for '{self._context}': {e}")

            # Cancel slow timer since we're now in failure/healing mode
            if feedback:
                feedback.cancel_slow_timer(self._page)

            # Check rate limit
            if not self._rate_limiter.can_make_call():
                logger.error(
                    f"Rate limit exceeded. Cannot heal locator for '{self._context}'"
                )
                raise  # Re-raise original error

            # START HEALING PROCESS WITH VISUAL FEEDBACK
            try:
                # STAGE 1: Analyzing page (replaces slow feedback if shown)
                if feedback:
                    feedback.show_stage(self._page, FeedbackStage.ANALYZING)

                # Capture screenshot (with caching)
                try:
                    screenshot_path = self._screenshot_cache.get_or_capture(self._page)
                except Exception as screenshot_error:
                    logger.error(f"Failed to capture screenshot: {screenshot_error}")
                    if feedback:
                        feedback.hide(self._page)
                    raise  # Re-raise original error

                # Get HTML snapshot - focus on body content
                try:
                    # Get body innerHTML instead of full page to skip CSS/scripts
                    body_locator = self._page.locator("body")
                    html_snapshot = body_locator.inner_html() if body_locator.count() > 0 else self._page.content()
                except Exception as html_error:
                    logger.error(f"Failed to get HTML snapshot: {html_error}")
                    if feedback:
                        feedback.hide(self._page)
                    raise  # Re-raise original error

                # STAGE 2: AI finding element
                if feedback:
                    feedback.show_stage(self._page, FeedbackStage.AI_FINDING)

                # Call Claude API
                self._rate_limiter.increment_call_count()
                logger.info(
                    f"Calling Claude API to heal locator for '{self._context}' "
                    f"(remaining calls: {self._rate_limiter.get_remaining_calls()})"
                )

                new_locator_str = self._claude_finder.find_locator(
                    screenshot_path=screenshot_path,
                    html_snapshot=html_snapshot,
                    element_description=self._context,
                    failed_locator=self._original_locator_str
                )

                if not new_locator_str:
                    logger.error(f"Claude could not find a locator for '{self._context}'")
                    if feedback:
                        feedback.hide(self._page)
                    raise  # Re-raise original error

                # Convert to Playwright Locator
                new_locator = self._claude_finder.locator_string_to_playwright(
                    self._page, new_locator_str
                )

                if not new_locator:
                    logger.error(f"Failed to convert locator string: {new_locator_str}")
                    if feedback:
                        feedback.hide(self._page)
                    raise  # Re-raise original error

                # STAGE 3: Testing solution
                if feedback:
                    feedback.show_stage(self._page, FeedbackStage.TESTING)

                # Test the new locator
                if not self._test_locator(new_locator):
                    logger.error(f"New locator failed validation: {new_locator_str}")
                    if feedback:
                        feedback.hide(self._page)
                    raise  # Re-raise original error

                # STAGE 4: Success!
                if feedback:
                    feedback.show_stage(self._page, FeedbackStage.SUCCESS)

                # Success! Save to cache and use it
                logger.info(f"Self-healing successful for '{self._context}': {new_locator_str}")
                self._cache.set(
                    self._cache_key,
                    new_locator_str,
                    original_locator=self._original_locator_str,
                    heal_count=1
                )
                self._locator = new_locator

                # Retry operation with healed locator
                method = getattr(self._locator, method_name)
                result = method(*args, **kwargs)

                # Brief success message, then hide
                if feedback:
                    self._page.wait_for_timeout(800)  # Show success for 800ms
                    feedback.hide(self._page)

                return result

            except Exception as healing_error:
                # Cleanup overlay on any failure
                if feedback:
                    feedback.hide(self._page)
                raise  # Re-raise the exception

    def _test_locator(self, locator: Locator) -> bool:
        """
        Test if a locator works by checking visibility.

        Args:
            locator: Locator to test.

        Returns:
            True if locator works, False otherwise.
        """
        try:
            # First check if element exists (count > 0)
            if locator.count() == 0:
                return False

            # Then verify it's attached
            locator.wait_for(state="attached", timeout=3000)
            return True
        except Exception as e:
            logger.debug(f"Locator validation failed: {e}")
            return False

    # Delegate all Locator methods with self-healing
    def click(self, **kwargs):
        """Click the element with self-healing."""
        return self._execute_with_healing("click", **kwargs)

    def fill(self, value: str, **kwargs):
        """Fill the element with self-healing."""
        return self._execute_with_healing("fill", value, **kwargs)

    def type(self, text: str, **kwargs):
        """Type text into the element with self-healing."""
        return self._execute_with_healing("type", text, **kwargs)

    def clear(self, **kwargs):
        """Clear the element with self-healing."""
        return self._execute_with_healing("clear", **kwargs)

    def check(self, **kwargs):
        """Check a checkbox with self-healing."""
        return self._execute_with_healing("check", **kwargs)

    def uncheck(self, **kwargs):
        """Uncheck a checkbox with self-healing."""
        return self._execute_with_healing("uncheck", **kwargs)

    def select_option(self, value=None, **kwargs):
        """Select an option with self-healing."""
        return self._execute_with_healing("select_option", value, **kwargs)

    def is_visible(self, **kwargs) -> bool:
        """Check if element is visible with self-healing."""
        return self._execute_with_healing("is_visible", **kwargs)

    def is_hidden(self, **kwargs) -> bool:
        """Check if element is hidden with self-healing."""
        return self._execute_with_healing("is_hidden", **kwargs)

    def is_enabled(self, **kwargs) -> bool:
        """Check if element is enabled with self-healing."""
        return self._execute_with_healing("is_enabled", **kwargs)

    def is_disabled(self, **kwargs) -> bool:
        """Check if element is disabled with self-healing."""
        return self._execute_with_healing("is_disabled", **kwargs)

    def is_editable(self, **kwargs) -> bool:
        """Check if element is editable with self-healing."""
        return self._execute_with_healing("is_editable", **kwargs)

    def is_checked(self, **kwargs) -> bool:
        """Check if checkbox is checked with self-healing."""
        return self._execute_with_healing("is_checked", **kwargs)

    def hover(self, **kwargs):
        """Hover over element with self-healing."""
        return self._execute_with_healing("hover", **kwargs)

    def focus(self, **kwargs):
        """Focus on element with self-healing."""
        return self._execute_with_healing("focus", **kwargs)

    def blur(self, **kwargs):
        """Blur element with self-healing."""
        return self._execute_with_healing("blur", **kwargs)

    def press(self, key: str, **kwargs):
        """Press a key with self-healing."""
        return self._execute_with_healing("press", key, **kwargs)

    def set_input_files(self, files, **kwargs):
        """Set input files with self-healing."""
        return self._execute_with_healing("set_input_files", files, **kwargs)

    def screenshot(self, **kwargs):
        """Take screenshot of element with self-healing."""
        return self._execute_with_healing("screenshot", **kwargs)

    def bounding_box(self, **kwargs):
        """Get bounding box with self-healing."""
        return self._execute_with_healing("bounding_box", **kwargs)

    def input_value(self, **kwargs) -> str:
        """Get input value with self-healing."""
        return self._execute_with_healing("input_value", **kwargs)

    def scroll_into_view_if_needed(self, **kwargs):
        """Scroll into view if needed with self-healing."""
        return self._execute_with_healing("scroll_into_view_if_needed", **kwargs)

    def set_checked(self, checked: bool, **kwargs):
        """Set checkbox state with self-healing."""
        return self._execute_with_healing("set_checked", checked, **kwargs)

    def tap(self, **kwargs):
        """Tap on element with self-healing."""
        return self._execute_with_healing("tap", **kwargs)

    def dispatch_event(self, type: str, event_init=None, **kwargs):
        """Dispatch event with self-healing."""
        if event_init is not None:
            return self._execute_with_healing("dispatch_event", type, event_init, **kwargs)
        return self._execute_with_healing("dispatch_event", type, **kwargs)

    def drag_to(self, target, **kwargs):
        """Drag element to target with self-healing."""
        # If target is a SelfHealingLocator, extract the underlying locator
        if isinstance(target, SelfHealingLocator):
            target = target._locator
        return self._execute_with_healing("drag_to", target, **kwargs)

    def wait_for(self, **kwargs):
        """Wait for element with self-healing."""
        return self._execute_with_healing("wait_for", **kwargs)

    def text_content(self, **kwargs) -> Optional[str]:
        """Get text content with self-healing."""
        return self._execute_with_healing("text_content", **kwargs)

    def inner_text(self, **kwargs) -> str:
        """Get inner text with self-healing."""
        return self._execute_with_healing("inner_text", **kwargs)

    def inner_html(self, **kwargs) -> str:
        """Get inner HTML with self-healing."""
        return self._execute_with_healing("inner_html", **kwargs)

    def get_attribute(self, name: str, **kwargs) -> Optional[str]:
        """Get attribute value with self-healing."""
        return self._execute_with_healing("get_attribute", name, **kwargs)

    def all_inner_texts(self, **kwargs):
        """Get all inner texts with self-healing."""
        return self._execute_with_healing("all_inner_texts", **kwargs)

    def all_text_contents(self, **kwargs):
        """Get all text contents with self-healing."""
        return self._execute_with_healing("all_text_contents", **kwargs)

    def evaluate(self, expression: str, arg=None, **kwargs):
        """Evaluate JavaScript expression with self-healing."""
        if arg is not None:
            return self._execute_with_healing("evaluate", expression, arg, **kwargs)
        return self._execute_with_healing("evaluate", expression, **kwargs)

    def count(self) -> int:
        """Get count of matching elements (no self-healing)."""
        return self._locator.count()

    def all(self):
        """
        Get all matching elements as a list of locators.

        Returns:
            List of SelfHealingLocator objects, one for each matching element.
        """
        all_locators = self._locator.all()
        return [
            SelfHealingLocator(
                loc,
                f"{self._context} (all:{i})",
                self._page,
                self._cache,
                self._rate_limiter,
                self._claude_finder,
                self._screenshot_cache,
                f"{self._cache_key}:all:{i}",
                enable_visual_feedback=self._enable_visual_feedback,
                slow_operation_threshold=self._slow_operation_threshold
            )
            for i, loc in enumerate(all_locators)
        ]

    @property
    def first(self):
        """Get first matching element."""
        first_locator = self._locator.first
        return SelfHealingLocator(
            first_locator,
            f"{self._context} (first)",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:first",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    @property
    def last(self):
        """Get last matching element."""
        last_locator = self._locator.last
        return SelfHealingLocator(
            last_locator,
            f"{self._context} (last)",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:last",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    def nth(self, index: int):
        """Get nth matching element."""
        nth_locator = self._locator.nth(index)
        return SelfHealingLocator(
            nth_locator,
            f"{self._context} (nth:{index})",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:nth:{index}",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    def filter(self, **kwargs):
        """Filter locator."""
        filtered_locator = self._locator.filter(**kwargs)
        return SelfHealingLocator(
            filtered_locator,
            f"{self._context} (filtered)",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:filtered",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    def locator(self, selector: str):
        """Create sub-locator."""
        sub_locator = self._locator.locator(selector)
        return SelfHealingLocator(
            sub_locator,
            f"{self._context} > {selector}",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:{selector}",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    def or_(self, locator):
        """
        Create a locator that matches either this locator or the provided locator.

        Args:
            locator: Another Locator or SelfHealingLocator to combine with OR logic.

        Returns:
            SelfHealingLocator with OR logic applied.
        """
        # If the input is a SelfHealingLocator, extract the underlying Playwright locator
        if isinstance(locator, SelfHealingLocator):
            other_locator = locator._locator
        else:
            other_locator = locator

        # Create OR locator using Playwright's .or_() method
        or_locator = self._locator.or_(other_locator)

        return SelfHealingLocator(
            or_locator,
            f"{self._context} OR {getattr(locator, '_context', str(locator))}",
            self._page,
            self._cache,
            self._rate_limiter,
            self._claude_finder,
            self._screenshot_cache,
            f"{self._cache_key}:or",
            enable_visual_feedback=self._enable_visual_feedback,
            slow_operation_threshold=self._slow_operation_threshold
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"SelfHealingLocator(context='{self._context}', locator={self._locator})"
