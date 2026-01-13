"""
Session management utilities for analytics tracking.
"""

import threading
import uuid
from datetime import datetime
from typing import Optional

_session_context = threading.local()


def generate_session_id(user_id: str, prefix: Optional[str] = None) -> str:
    """Generate unique session ID: {prefix}-{user_id}-{timestamp}-{uuid8}"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique = str(uuid.uuid4())[:8]
    parts = [p for p in [prefix, user_id, timestamp, unique] if p]
    return "-".join(parts)


def get_current_session_id() -> Optional[str]:
    """Get session_id from thread-local storage"""
    return getattr(_session_context, 'session_id', None)


def set_current_session_id(session_id: Optional[str]) -> None:
    """Set session_id in thread-local storage"""
    _session_context.session_id = session_id


class SessionContext:
    """Context manager for automatic session lifecycle"""
    def __init__(self, client, user_id: str, session_id: Optional[str] = None, mcp_name: Optional[str] = None):
        self.client = client
        self.user_id = user_id
        self.session_id = session_id
        self.mcp_name = mcp_name
    
    def __enter__(self) -> str:
        self.session_id = self.client.track_session_start(self.user_id, self.session_id, mcp_name=self.mcp_name)
        return self.session_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.track_session_end(self.user_id, self.session_id, mcp_name=self.mcp_name)

