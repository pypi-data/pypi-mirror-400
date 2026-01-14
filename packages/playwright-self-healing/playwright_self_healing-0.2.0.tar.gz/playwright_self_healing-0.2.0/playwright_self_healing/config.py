"""Configuration management for playwright-self-healing."""

import os
import logging
from typing import Optional, Tuple


logger = logging.getLogger(__name__)


class SelfHealingConfig:
    """Configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.enabled: bool = os.getenv("ENABLE_SELF_HEALING", "false").lower() == "true"
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")
        self.max_retries: int = int(os.getenv("SELF_HEALING_MAX_RETRIES", "3"))
        self.screenshot_cache_ttl: int = int(os.getenv("SCREENSHOT_CACHE_TTL", "30"))
        self.cache_dir: str = os.getenv("SELF_HEALING_CACHE_DIR", ".cache")
        self.debug: bool = os.getenv("SELF_HEALING_DEBUG", "false").lower() == "true"

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, error_message).
            If valid, error_message is None.
        """
        if not self.enabled:
            return False, (
                "Self-healing is disabled. Set ENABLE_SELF_HEALING=true to activate.\n"
                "WARNING: This will send page screenshots and HTML to Anthropic's API for locator healing."
            )

        if not self.anthropic_api_key:
            return False, "Self-healing is enabled, but ANTHROPIC_API_KEY environment variable is not set"

        if self.max_retries < 0:
            return False, f"SELF_HEALING_MAX_RETRIES must be non-negative, got {self.max_retries}"

        if self.screenshot_cache_ttl < 0:
            return False, f"SCREENSHOT_CACHE_TTL must be non-negative, got {self.screenshot_cache_ttl}"

        return True, None


# Global config instance
_config: Optional[SelfHealingConfig] = None


def get_config() -> SelfHealingConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = SelfHealingConfig()
    return _config
