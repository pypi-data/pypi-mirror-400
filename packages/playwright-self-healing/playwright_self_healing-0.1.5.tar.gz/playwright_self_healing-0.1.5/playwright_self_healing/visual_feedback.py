"""Visual feedback overlay for self-healing operations."""

import logging
from enum import Enum
from typing import Optional
from playwright.sync_api import Page


logger = logging.getLogger(__name__)


class FeedbackStage(Enum):
    """Stages of the self-healing process with their display messages and colors."""
    WAITING = ("⏱ Locator taking longer than expected...", "#7A6B5B")  # Professional amber/brown
    ANALYZING = ("Analyzing page...", "#5B6B7A")  # Professional slate gray
    AI_FINDING = ("🧠 AI analyzing element...", "#4B6B9A")  # Professional deep blue
    TESTING = ("Testing solution...", "#6B7B8A")  # Muted blue-gray
    SUCCESS = ("✓ Self-healing complete", "#4A7C59")  # Professional forest green


class VisualFeedback:
    """
    Manages visual feedback overlay during self-healing operations.

    Provides non-intrusive banner notifications at the top of the page
    to inform users about the self-healing process stages.
    """

    OVERLAY_ID = "playwright-self-healing-overlay"

    def __init__(self):
        """Initialize visual feedback manager."""
        pass

    def show_stage(self, page: Page, stage: FeedbackStage) -> bool:
        """
        Show or update the overlay with the specified stage.

        Args:
            page: Playwright Page object
            stage: FeedbackStage to display

        Returns:
            True if successful, False if failed (non-critical)
        """
        try:
            message, color = stage.value
            js_code = self._get_overlay_js(message, color)
            page.evaluate(js_code)
            logger.debug(f"Visual feedback: {message}")
            return True
        except Exception as e:
            logger.debug(f"Failed to show visual feedback (non-critical): {e}")
            return False

    def hide(self, page: Page) -> bool:
        """
        Remove the overlay from the page.

        Args:
            page: Playwright Page object

        Returns:
            True if successful, False if failed (non-critical)
        """
        try:
            js_code = f"""
                (() => {{
                    const overlay = document.getElementById('{self.OVERLAY_ID}');
                    if (overlay) {{
                        overlay.style.opacity = '0';
                        setTimeout(() => overlay.remove(), 300);
                    }}
                    // Clear any pending slow operation timer
                    if (window.__playwrightSelfHealingSlowTimer) {{
                        clearTimeout(window.__playwrightSelfHealingSlowTimer);
                        delete window.__playwrightSelfHealingSlowTimer;
                    }}
                }})();
            """
            page.evaluate(js_code)
            logger.debug("Visual feedback hidden")
            return True
        except Exception as e:
            logger.debug(f"Failed to hide visual feedback (non-critical): {e}")
            return False

    def start_slow_timer(self, page: Page, threshold_ms: int) -> bool:
        """
        Start a browser-side timer to show slow operation feedback.

        Args:
            page: Playwright Page object
            threshold_ms: Milliseconds before showing slow operation message

        Returns:
            True if successful, False if failed (non-critical)
        """
        try:
            message, color = FeedbackStage.WAITING.value
            js_code = f"""
                (() => {{
                    // Clear any existing timer
                    if (window.__playwrightSelfHealingSlowTimer) {{
                        clearTimeout(window.__playwrightSelfHealingSlowTimer);
                    }}

                    // Start new timer
                    window.__playwrightSelfHealingSlowTimer = setTimeout(() => {{
                        {self._get_overlay_js(message, color)}
                        delete window.__playwrightSelfHealingSlowTimer;
                    }}, {threshold_ms});
                }})();
            """
            page.evaluate(js_code)
            logger.debug(f"Started slow operation timer ({threshold_ms}ms)")
            return True
        except Exception as e:
            logger.debug(f"Failed to start slow operation timer (non-critical): {e}")
            return False

    def cancel_slow_timer(self, page: Page) -> bool:
        """
        Cancel the slow operation timer.

        Args:
            page: Playwright Page object

        Returns:
            True if successful, False if failed (non-critical)
        """
        try:
            js_code = """
                (() => {
                    if (window.__playwrightSelfHealingSlowTimer) {
                        clearTimeout(window.__playwrightSelfHealingSlowTimer);
                        delete window.__playwrightSelfHealingSlowTimer;
                    }
                })();
            """
            page.evaluate(js_code)
            logger.debug("Cancelled slow operation timer")
            return True
        except Exception as e:
            logger.debug(f"Failed to cancel slow operation timer (non-critical): {e}")
            return False

    def _get_overlay_js(self, message: str, color: str) -> str:
        """
        Generate JavaScript code to create/update the overlay.

        Args:
            message: Message to display
            color: Background color (hex)

        Returns:
            JavaScript code as string
        """
        return f"""
            (() => {{
                const OVERLAY_ID = '{self.OVERLAY_ID}';
                let overlay = document.getElementById(OVERLAY_ID);

                if (!overlay) {{
                    // Create new overlay
                    overlay = document.createElement('div');
                    overlay.id = OVERLAY_ID;
                    overlay.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        z-index: 2147483647;
                        background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                        color: #ffffff;
                        padding: 14px 24px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                        font-size: 13px;
                        font-weight: 600;
                        letter-spacing: 0.3px;
                        text-align: center;
                        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
                        box-shadow: 0 2px 12px rgba(0,0,0,0.2), 0 1px 3px rgba(0,0,0,0.1);
                        border-bottom: 1px solid rgba(255,255,255,0.1);
                        opacity: 0;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        pointer-events: none;
                        backdrop-filter: blur(8px);
                    `;
                    document.body.appendChild(overlay);

                    // Trigger fade-in
                    setTimeout(() => {{ overlay.style.opacity = '1'; }}, 10);
                }} else {{
                    // Update existing overlay
                    overlay.style.background = `linear-gradient(135deg, {color} 0%, {color}dd 100%)`;
                    overlay.style.opacity = '1';
                }}

                overlay.textContent = '{message}';
            }})();
        """


# Global singleton instance
_feedback_instance: Optional[VisualFeedback] = None


def get_visual_feedback() -> VisualFeedback:
    """Get or create the global VisualFeedback instance."""
    global _feedback_instance
    if _feedback_instance is None:
        _feedback_instance = VisualFeedback()
    return _feedback_instance
