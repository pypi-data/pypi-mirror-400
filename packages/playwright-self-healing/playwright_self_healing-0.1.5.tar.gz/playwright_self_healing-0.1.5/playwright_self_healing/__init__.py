"""
playwright-self-healing: AI-powered self-healing locators for Playwright Python tests.

Main exports:
    - SelfHealingPage: Wrap a Playwright Page to add self-healing capabilities
    - get_config: Get configuration instance
    - VisualFeedback: Visual overlay manager for self-healing operations
    - FeedbackStage: Enum of feedback stages
"""

from .page_wrapper import SelfHealingPage
from .config import get_config, SelfHealingConfig
from .version import __version__
from .locator_wrapper import SelfHealingLocator
from .visual_feedback import VisualFeedback, FeedbackStage

# Monkey-patch Playwright's expect() to handle SelfHealingLocators automatically
# This allows users to continue using `from playwright.sync_api import expect` without changes
import playwright.sync_api as pw_sync_api
import sys

# Store the original expect function
_original_playwright_expect = pw_sync_api.expect


def _patched_expect(locator_or_page):
    """
    Patched version of Playwright's expect() that automatically handles SelfHealingLocators.

    This is transparent to users - they can continue using:
        from playwright.sync_api import expect
        expect(locator).to_be_visible()

    Even with SelfHealingLocators, without any code changes!
    """
    # If it's a SelfHealingLocator, unwrap it to get the underlying Playwright Locator
    if isinstance(locator_or_page, SelfHealingLocator):
        return _original_playwright_expect(locator_or_page._locator)

    # Otherwise, pass it through to Playwright's original expect
    return _original_playwright_expect(locator_or_page)


# Replace Playwright's expect with our patched version in multiple places
pw_sync_api.expect = _patched_expect

# Also patch in the sys.modules cache to catch any early imports
if 'playwright.sync_api' in sys.modules:
    sys.modules['playwright.sync_api'].expect = _patched_expect

# Export from this module for convenience
expect = _patched_expect


__all__ = [
    "SelfHealingPage",
    "expect",
    "get_config",
    "SelfHealingConfig",
    "VisualFeedback",
    "FeedbackStage",
    "__version__"
]
