"""Pytest configuration and fixtures for tests."""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set a dummy API key for tests (will be mocked)
    os.environ["ANTHROPIC_API_KEY"] = "test-key-12345"
    os.environ["SELF_HEALING_DEBUG"] = "true"
    yield
    # Cleanup
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]
