"""Tests for configuration."""

import os
from playwright_self_healing.config import SelfHealingConfig


def test_config_validation_with_api_key():
    """Test configuration validation with API key."""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"

    config = SelfHealingConfig()
    is_valid, error = config.validate()

    assert is_valid is True
    assert error is None


def test_config_validation_without_api_key():
    """Test configuration validation without API key."""
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

    config = SelfHealingConfig()
    is_valid, error = config.validate()

    assert is_valid is False
    assert "ANTHROPIC_API_KEY" in error


def test_config_defaults():
    """Test default configuration values."""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"

    config = SelfHealingConfig()

    assert config.claude_model == "claude-sonnet-4.5"
    assert config.max_retries == 3
    assert config.screenshot_cache_ttl == 30
    assert config.cache_dir == ".cache"
    assert config.debug is False


def test_config_custom_values():
    """Test custom configuration values from environment."""
    os.environ["ANTHROPIC_API_KEY"] = "custom-key"
    os.environ["CLAUDE_MODEL"] = "claude-opus-4"
    os.environ["SELF_HEALING_MAX_RETRIES"] = "10"
    os.environ["SCREENSHOT_CACHE_TTL"] = "60"
    os.environ["SELF_HEALING_CACHE_DIR"] = "/tmp/cache"
    os.environ["SELF_HEALING_DEBUG"] = "true"

    config = SelfHealingConfig()

    assert config.anthropic_api_key == "custom-key"
    assert config.claude_model == "claude-opus-4"
    assert config.max_retries == 10
    assert config.screenshot_cache_ttl == 60
    assert config.cache_dir == "/tmp/cache"
    assert config.debug is True

    # Cleanup
    del os.environ["CLAUDE_MODEL"]
    del os.environ["SELF_HEALING_MAX_RETRIES"]
    del os.environ["SCREENSHOT_CACHE_TTL"]
    del os.environ["SELF_HEALING_CACHE_DIR"]
    del os.environ["SELF_HEALING_DEBUG"]
