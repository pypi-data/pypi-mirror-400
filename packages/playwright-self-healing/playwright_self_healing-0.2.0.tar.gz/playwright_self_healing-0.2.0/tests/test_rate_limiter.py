"""Tests for rate limiter."""

import os
import tempfile
from playwright_self_healing.rate_limiter import RateLimiter


def test_rate_limiter_enforcement():
    """Test rate limit enforcement."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        session_file = f.name

    try:
        limiter = RateLimiter(max_calls=3, session_file=session_file)
        limiter.reset_session()

        # Should allow 3 calls
        assert limiter.can_make_call() is True
        limiter.increment_call_count()

        assert limiter.can_make_call() is True
        limiter.increment_call_count()

        assert limiter.can_make_call() is True
        limiter.increment_call_count()

        # Should block 4th call
        assert limiter.can_make_call() is False

    finally:
        if os.path.exists(session_file):
            os.remove(session_file)


def test_remaining_calls():
    """Test remaining calls calculation."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        session_file = f.name

    try:
        limiter = RateLimiter(max_calls=5, session_file=session_file)
        limiter.reset_session()

        assert limiter.get_remaining_calls() == 5

        limiter.increment_call_count()
        assert limiter.get_remaining_calls() == 4

        limiter.increment_call_count()
        assert limiter.get_remaining_calls() == 3

    finally:
        if os.path.exists(session_file):
            os.remove(session_file)


def test_session_reset():
    """Test session reset."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        session_file = f.name

    try:
        limiter = RateLimiter(max_calls=3, session_file=session_file)
        limiter.reset_session()

        # Use all calls
        limiter.increment_call_count()
        limiter.increment_call_count()
        limiter.increment_call_count()
        assert limiter.can_make_call() is False

        # Reset
        limiter.reset_session()
        assert limiter.can_make_call() is True
        assert limiter.get_remaining_calls() == 3

    finally:
        if os.path.exists(session_file):
            os.remove(session_file)


def test_rate_limiter_stats():
    """Test rate limiter statistics."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        session_file = f.name

    try:
        limiter = RateLimiter(max_calls=5, session_file=session_file)
        limiter.reset_session()

        limiter.increment_call_count()
        limiter.increment_call_count()

        stats = limiter.get_stats()
        assert stats["call_count"] == 2
        assert stats["max_calls"] == 5
        assert stats["remaining_calls"] == 3

    finally:
        if os.path.exists(session_file):
            os.remove(session_file)
