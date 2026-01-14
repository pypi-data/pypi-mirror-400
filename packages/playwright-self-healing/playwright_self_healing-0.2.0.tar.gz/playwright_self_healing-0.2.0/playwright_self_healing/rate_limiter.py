"""Rate limiting for Claude API calls."""

import os
import json
import threading
from datetime import datetime
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Tracks LLM API usage per test session.
    Prevents excessive API calls during a single test run.
    """

    def __init__(self, max_calls: int = 10, session_file: str = ".temp/self_healing_session.json"):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of Claude API calls per session.
            session_file: Path to session tracking file.
        """
        self.max_calls = max_calls
        self.session_file = session_file
        self.lock = threading.Lock()
        self._ensure_session_file_exists()

    def _ensure_session_file_exists(self):
        """Create session directory and file if they don't exist."""
        session_dir = os.path.dirname(self.session_file)
        if session_dir and not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)

    def can_make_call(self) -> bool:
        """
        Check if another Claude API call is allowed in this session.

        Returns:
            True if another call is allowed, False otherwise.
        """
        with self.lock:
            count = self._get_call_count()
            can_call = count < self.max_calls
            if not can_call:
                logger.warning(
                    f"Rate limit reached: {count}/{self.max_calls} calls used"
                )
            return can_call

    def increment_call_count(self):
        """Record a new Claude API call in the session."""
        with self.lock:
            data = self._load_session()
            data["call_count"] = data.get("call_count", 0) + 1
            data["last_call"] = datetime.utcnow().isoformat() + "Z"
            self._save_session(data)
            logger.info(
                f"Claude API call recorded: {data['call_count']}/{self.max_calls}"
            )

    def get_remaining_calls(self) -> int:
        """
        Get the number of remaining allowed calls.

        Returns:
            Number of remaining API calls.
        """
        with self.lock:
            count = self._get_call_count()
            return max(0, self.max_calls - count)

    def reset_session(self):
        """Reset the session counter (called at test session start)."""
        with self.lock:
            self._save_session({
                "call_count": 0,
                "session_start": datetime.utcnow().isoformat() + "Z"
            })
            logger.info("Rate limiter session reset")

    def _get_call_count(self) -> int:
        """Get current call count from session file."""
        data = self._load_session()
        return data.get("call_count", 0)

    def _load_session(self) -> Dict[str, Any]:
        """Load session data from JSON file."""
        if not os.path.exists(self.session_file):
            return {}

        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return {}

    def _save_session(self, data: Dict[str, Any]):
        """Save session data to JSON file."""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with session stats.
        """
        with self.lock:
            data = self._load_session()
            call_count = data.get("call_count", 0)
            return {
                "call_count": call_count,
                "max_calls": self.max_calls,
                "remaining_calls": max(0, self.max_calls - call_count),
                "session_start": data.get("session_start"),
                "last_call": data.get("last_call")
            }
