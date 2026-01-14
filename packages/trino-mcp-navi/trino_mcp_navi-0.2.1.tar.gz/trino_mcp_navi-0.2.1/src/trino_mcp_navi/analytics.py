#!/usr/bin/env python3
"""
Analytics module for Trino MCP Server.
Tracks tool usage to understand how the server is being used.

Privacy: Only tracks tool names and success/failure. 
No query content or sensitive data is captured.
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

# PostHog configuration
# Default key sends analytics to the package maintainer's dashboard
# Users can override with their own key via POSTHOG_API_KEY env var
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "phc_QZq05SGLWLp407jyMh6Kjk1szDWolUPqsXjCrxgTric")
ANALYTICS_ENABLED = os.getenv("TRINO_MCP_ANALYTICS", "true").lower() == "true"

# Initialize PostHog client
_posthog_client = None


def _get_posthog():
    """Lazy initialize PostHog client."""
    global _posthog_client
    if _posthog_client is None and ANALYTICS_ENABLED:
        try:
            import posthog
            posthog.api_key = POSTHOG_API_KEY
            posthog.host = "https://app.posthog.com"
            _posthog_client = posthog
            logger.debug("PostHog analytics initialized")
        except Exception as e:
            logger.debug(f"PostHog not available: {e}")
            _posthog_client = False  # Mark as failed
    return _posthog_client if _posthog_client else None


def _get_anonymous_user_id() -> str:
    """
    Generate an anonymous user ID based on machine/user info.
    This is a hash - no PII is stored or transmitted.
    """
    # Create a hash from username and host (anonymized)
    user = os.getenv("TRINO_USER", "unknown")
    host = os.getenv("TRINO_HOST", "unknown")
    raw = f"{user}:{host}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def track_event(
    event_name: str,
    properties: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track an analytics event.
    
    Args:
        event_name: Name of the event (e.g., "tool_called")
        properties: Additional properties to track
    """
    if not ANALYTICS_ENABLED:
        return
    
    posthog = _get_posthog()
    if not posthog:
        return
    
    try:
        user_id = _get_anonymous_user_id()
        event_props = {
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_version": "0.1.0",
            **(properties or {})
        }
        
        posthog.capture(
            distinct_id=user_id,
            event=event_name,
            properties=event_props
        )
        logger.debug(f"Tracked event: {event_name}")
    except Exception as e:
        # Never let analytics break the main functionality
        logger.debug(f"Analytics error (ignored): {e}")


def track_tool_call(tool_name: str):
    """
    Decorator to track tool calls.
    
    Usage:
        @track_tool_call("my_tool")
        def my_tool():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = True
            error_type = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
            finally:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                track_event("tool_called", {
                    "tool_name": tool_name,
                    "success": success,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": error_type,
                    # Track which arguments were provided (not their values)
                    "args_provided": list(kwargs.keys()) if kwargs else []
                })
        
        return wrapper
    return decorator


def track_server_start():
    """Track when the server starts."""
    track_event("server_started", {
        "transport": os.getenv("MCP_TRANSPORT", "stdio"),
        "catalog": os.getenv("TRINO_CATALOG", "unknown"),
    })


def track_server_stop():
    """Track when the server stops."""
    track_event("server_stopped")
