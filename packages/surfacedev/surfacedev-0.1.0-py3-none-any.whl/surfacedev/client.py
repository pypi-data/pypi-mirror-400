"""
Analytics Client for Supabase integration.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
from supabase import create_client, Client
from .config import AnalyticsConfig
from .session import get_current_session_id, set_current_session_id, generate_session_id

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """
    Client for tracking and sending analytics events to Supabase.
    
    Usage:
        config = AnalyticsConfig.from_env()
        client = AnalyticsClient(config)
        client.track(user_id="user123", event_name="tool_used", metadata={"tool": "get_benchmarks"})
    """
    
    def __init__(self, config: AnalyticsConfig):
        """
        Initialize analytics client.
        
        Args:
            config: Analytics configuration object.
        """
        self.config = config
        self.supabase: Optional[Client] = None
        
        if config.is_configured:
            try:
                self.supabase = create_client(config.supabase_url, config.supabase_key)
                logger.info(f"Analytics client initialized with Supabase table: {config.table_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.supabase = None
        else:
            logger.warning("Analytics not configured. Event tracking will be disabled.")
    
    def _ensure_client(self):
        """Ensure Supabase client is initialized."""
        if not self.supabase:
            raise ValueError("Supabase client is not initialized. Check your configuration.")
    
    def track(
        self,
        user_id: str,
        event_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        session_id: Optional[str] = None,
        mcp_name: Optional[str] = None
    ) -> bool:
        """
        Track an event and send it to Supabase.
        
        Args:
            user_id: Unique identifier for the user.
            event_name: Name of the event (e.g., "tool_used", "error_occurred").
            metadata: Optional dictionary with additional event data.
            timestamp: Optional event timestamp (defaults to current time).
            session_id: Optional session ID for grouping events into chains.
            mcp_name: Optional MCP server name (e.g., "drea", "benchmark-mcp").
        
        Returns:
            True if event was sent successfully, False otherwise.
        """
        if not self.config.is_configured or not self.supabase:
            logger.debug("Analytics not configured, skipping event tracking")
            return False
        
        if not user_id or not event_name:
            logger.warning("user_id and event_name are required for tracking")
            return False
        
        # Auto-retrieve session_id from thread-local if not provided
        if session_id is None:
            session_id = get_current_session_id()
        
        try:
            self._ensure_client()
            
            # Prepare event payload
            event_data = {
                "user_id": user_id,
                "event_name": event_name,
                "metadata": metadata or {},
                "created_at": (timestamp or datetime.utcnow()).isoformat(),
                "session_id": session_id,
                "mcp_name": mcp_name,
            }
            
            # Insert into Supabase table
            # Supabase insert() returns the inserted data by default if successful
            response = self.supabase.table(self.config.table_name).insert(event_data).execute()
            
            # Check if insert was successful
            # Supabase returns the inserted data in response.data if successful
            # If response.data is empty or None, the insert might still have succeeded
            # (this can happen with RLS or if the client doesn't return data)
            if response is not None:
                if response.data and len(response.data) > 0:
                    inserted_id = response.data[0].get('id', 'unknown')
                    logger.debug(f"Successfully tracked event: {event_name} for user: {user_id}, inserted_id: {inserted_id}")
                else:
                    # Insert likely succeeded (no exception was raised)
                    # Empty response.data can be normal - the data is still inserted
                    logger.debug(f"Successfully tracked event: {event_name} for user: {user_id} (insert completed)")
                return True
            else:
                logger.warning(f"Event tracked but response is None: {event_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to track event {event_name} for user {user_id}: {e}", exc_info=True)
            return False
    
    def track_tool_usage(
        self,
        user_id: str,
        tool_name: str,
        tool_params: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        session_id: Optional[str] = None,
        mcp_name: Optional[str] = None
    ) -> bool:
        """
        Convenience method to track MCP tool usage.
        
        Args:
            user_id: Unique identifier for the user.
            tool_name: Name of the MCP tool that was called.
            tool_params: Parameters passed to the tool.
            success: Whether the tool execution was successful.
            error_message: Error message if execution failed.
            execution_time_ms: Tool execution time in milliseconds.
        
        Returns:
            True if event was sent successfully, False otherwise.
        """
        metadata = {
            "tool_name": tool_name,
            "success": success,
        }
        
        if tool_params:
            # Sanitize parameters (remove sensitive data, limit size)
            sanitized_params = self._sanitize_metadata(tool_params)
            metadata["tool_params"] = sanitized_params
        
        if error_message:
            metadata["error_message"] = error_message[:500]  # Limit error message length
        
        if execution_time_ms is not None:
            metadata["execution_time_ms"] = execution_time_ms
        
        return self.track(
            user_id=user_id,
            event_name=tool_name,
            metadata=metadata,
            session_id=session_id,
            mcp_name=mcp_name
        )
    
    def _sanitize_metadata(self, data: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
        """
        Sanitize metadata to prevent sending overly large or sensitive data.
        
        Args:
            data: Metadata dictionary to sanitize.
            max_depth: Maximum nesting depth.
        
        Returns:
            Sanitized metadata dictionary.
        """
        if max_depth <= 0:
            return {"_truncated": True}
        
        sanitized = {}
        for key, value in data.items():
            # Skip sensitive keys
            if any(sensitive in key.lower() for sensitive in ["password", "secret", "key", "token", "auth"]):
                sanitized[key] = "[REDACTED]"
                continue
            
            # Handle different types
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_metadata(value, max_depth - 1)
            elif isinstance(value, (list, tuple)):
                # Limit list size
                sanitized[key] = list(value[:10]) if len(value) > 10 else list(value)
            elif isinstance(value, str):
                # Limit string length
                sanitized[key] = value[:500] if len(value) > 500 else value
            else:
                sanitized[key] = value
        
        return sanitized
    
    def batch_track(
        self,
        events: list[Dict[str, Any]],
        session_id: Optional[str] = None,
        mcp_name: Optional[str] = None
    ) -> bool:
        """
        Track multiple events in a single batch insert.
        
        Args:
            events: List of event dictionaries, each containing:
                - user_id: str
                - event_name: str
                - metadata: Optional[Dict[str, Any]]
                - timestamp: Optional[datetime]
                - session_id: Optional[str] (can override batch session_id)
                - mcp_name: Optional[str] (can override batch mcp_name)
            session_id: Optional session ID to apply to all events in batch.
            mcp_name: Optional MCP name to apply to all events in batch.
        
        Returns:
            True if all events were sent successfully, False otherwise.
        """
        if not self.config.is_configured or not self.supabase:
            logger.debug("Analytics not configured, skipping batch event tracking")
            return False
        
        # Auto-retrieve session_id from thread-local if not provided
        if session_id is None:
            session_id = get_current_session_id()
        
        try:
            self._ensure_client()
            
            # Prepare events for batch insert
            batch_data = []
            for event in events:
                if not event.get("user_id") or not event.get("event_name"):
                    logger.warning("Skipping event without user_id or event_name")
                    continue
                
                # Use event's session_id/mcp_name if provided, otherwise use batch values
                event_session_id = event.get("session_id", session_id)
                event_mcp_name = event.get("mcp_name", mcp_name)
                
                batch_data.append({
                    "user_id": event["user_id"],
                    "event_name": event["event_name"],
                    "metadata": event.get("metadata", {}),
                    "created_at": (event.get("timestamp") or datetime.utcnow()).isoformat(),
                    "session_id": event_session_id,
                    "mcp_name": event_mcp_name,
                })
            
            if not batch_data:
                logger.warning("No valid events to track")
                return False
            
            # Batch insert into Supabase
            response = self.supabase.table(self.config.table_name).insert(batch_data).execute()
            
            # Check if insert was successful
            if response is not None:
                if response.data and len(response.data) > 0:
                    logger.debug(f"Successfully tracked {len(batch_data)} events in batch, got {len(response.data)} rows back")
                else:
                    # Insert likely succeeded (no exception was raised)
                    # Empty response.data can be normal - the data is still inserted
                    logger.debug(f"Successfully tracked {len(batch_data)} events in batch (insert completed)")
                return True
            else:
                logger.warning("Batch events tracked but response is None")
                return False
                
        except Exception as e:
            logger.error(f"Failed to track batch events: {e}")
            return False
    
    def track_session_start(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mcp_name: Optional[str] = None
    ) -> str:
        """Start session, track 'session_start' event, store in thread-local"""
        if session_id is None:
            session_id = generate_session_id(user_id)
        
        set_current_session_id(session_id)
        self.track(
            user_id=user_id,
            event_name="session_start",
            metadata=metadata,
            session_id=session_id,
            mcp_name=mcp_name
        )
        return session_id
    
    def track_session_end(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mcp_name: Optional[str] = None
    ) -> bool:
        """End session, track 'session_end' event, clear thread-local"""
        if session_id is None:
            session_id = get_current_session_id()
        
        result = self.track(
            user_id=user_id,
            event_name="session_end",
            metadata=metadata,
            session_id=session_id,
            mcp_name=mcp_name
        )
        set_current_session_id(None)
        return result
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session_id from thread-local"""
        return get_current_session_id()
    
    def track_tool_call_with_session(
        self,
        tool_name: str,
        user_id: str = "anonymous",
        success: bool = True,
        execution_time_ms: float = 0,
        error_message: Optional[str] = None,
        tool_params: Optional[Dict[str, Any]] = None,
        mcp_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Track a tool call with analytics, automatically creating a session for the call.
        This is a convenience method that starts a session, tracks the tool usage, and ends the session.
        
        Args:
            tool_name: Name of the tool being called
            user_id: User identifier (defaults to "anonymous")
            success: Whether the tool call was successful
            execution_time_ms: Tool execution time in milliseconds
            error_message: Error message if the call failed
            tool_params: Optional parameters passed to the tool
            mcp_name: Optional MCP server name
            
        Returns:
            Session ID if tracking succeeded, None otherwise
        """
        if not self.config.is_configured or not self.supabase:
            return None
        
        try:
            # Start a session for this tool call
            session_id = self.track_session_start(
                user_id=user_id,
                mcp_name=mcp_name,
                metadata={"tool": tool_name}
            )
            
            # Track the tool usage
            self.track_tool_usage(
                user_id=user_id,
                tool_name=tool_name,
                tool_params=tool_params,
                success=success,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                session_id=session_id,
                mcp_name=mcp_name
            )
            
            # End the session
            self.track_session_end(
                user_id=user_id,
                session_id=session_id,
                mcp_name=mcp_name
            )
            
            return session_id
        except Exception as e:
            logger.warning(f"Failed to track tool call: {e}")
            return None
    
    def get_session_events(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all events for a session (the chain), ordered by timestamp"""
        if not self.config.is_configured or not self.supabase:
            return []
        
        try:
            self._ensure_client()
            query = self.supabase.table(self.config.table_name)\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)
            
            if user_id:
                query = query.eq("user_id", user_id)
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get session events: {e}")
            return []
    
    def get_session_summary(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate chain metrics: count, duration, success rate, errors"""
        events = self.get_session_events(session_id, user_id)
        
        if not events:
            return {"session_id": session_id, "event_count": 0}
        
        try:
            timestamps = [datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")) for e in events]
            duration_ms = (max(timestamps) - min(timestamps)).total_seconds() * 1000
        except Exception:
            duration_ms = 0
        
        success_count = sum(1 for e in events if e.get("metadata", {}).get("success") is True)
        error_count = sum(1 for e in events if e.get("metadata", {}).get("error_message"))
        
        return {
            "session_id": session_id,
            "event_count": len(events),
            "duration_ms": duration_ms,
            "success_rate": success_count / len(events) if events else 0,
            "error_count": error_count,
            "first_event": events[0]["created_at"],
            "last_event": events[-1]["created_at"]
        }
    
    def get_user_sessions(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user with summary stats"""
        if not self.config.is_configured or not self.supabase:
            return []
        
        try:
            self._ensure_client()
            query = self.supabase.table(self.config.table_name)\
                .select("session_id, created_at")\
                .eq("user_id", user_id)\
                .not_.is_("session_id", "null")\
                .order("created_at", desc=True)
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            if limit:
                query = query.limit(limit * 100)  # Over-fetch, then group
            
            response = query.execute()
            if not response.data:
                return []
            
            # Group by session_id and calculate summaries
            sessions = defaultdict(list)
            for event in response.data:
                sessions[event["session_id"]].append(event)
            
            result = []
            for sid, events in sessions.items():
                try:
                    timestamps = [datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")) for e in events]
                    result.append({
                        "session_id": sid,
                        "event_count": len(events),
                        "started_at": min(timestamps).isoformat(),
                        "ended_at": max(timestamps).isoformat(),
                        "duration_ms": (max(timestamps) - min(timestamps)).total_seconds() * 1000
                    })
                except Exception:
                    continue
            
            return sorted(result, key=lambda x: x["started_at"], reverse=True)[:limit] if limit else result
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

