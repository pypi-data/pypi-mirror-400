"""
Analytics tracking for Tableau MCP Server.
Uses PostHog for anonymous usage analytics.
"""

import os
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("tableau-mcp.analytics")

# PostHog configuration
# Default key sends analytics to the package maintainer's dashboard
# Users can override with their own key via POSTHOG_API_KEY env var
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "phc_QZq05SGLWLp407jyMh6Kjk1szDWolUPqsXjCrxgTric")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")

# Check if analytics is disabled
ANALYTICS_ENABLED = os.getenv("TABLEAU_MCP_ANALYTICS", "true").lower() != "false"

# Initialize PostHog
_posthog_client = None

if ANALYTICS_ENABLED and POSTHOG_API_KEY:
    try:
        import posthog
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST
        _posthog_client = posthog
        logger.info(f"PostHog analytics initialized")
    except ImportError:
        logger.warning("PostHog not installed, analytics disabled")
    except Exception as e:
        logger.warning(f"Failed to initialize PostHog: {e}")


def _get_anonymous_id() -> str:
    """Generate an anonymous ID based on environment."""
    import hashlib
    
    # Create a hash from server URL + token name for consistent ID
    server_url = os.getenv("TABLEAU_SERVER_URL", "unknown")
    token_name = os.getenv("TABLEAU_TOKEN_NAME", os.getenv("TABLEAU_USERNAME", "unknown"))
    
    unique_string = f"{server_url}:{token_name}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16]


def track_event(event_name: str, properties: Optional[Dict[str, Any]] = None):
    """
    Track an analytics event.
    
    Args:
        event_name: Name of the event
        properties: Optional properties dict
    """
    if not _posthog_client or not ANALYTICS_ENABLED:
        return
    
    try:
        distinct_id = _get_anonymous_id()
        
        full_properties = {
            "mcp_server": "tableau-mcp-navi",
            "server_url_hash": _get_anonymous_id(),
            **(properties or {})
        }
        
        _posthog_client.capture(distinct_id, event_name, full_properties)
        
    except Exception as e:
        logger.debug(f"Failed to track event {event_name}: {e}")


def track_server_start():
    """Track server startup."""
    track_event("server_started", {
        "transport": "stdio"
    })


def track_tool_call(tool_name: str):
    """
    Decorator to track tool usage.
    
    Args:
        tool_name: Name of the tool being tracked
    """
    def decorator(func: Callable) -> Callable:
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
                    "args_provided": list(kwargs.keys()) if kwargs else []
                })
        
        return wrapper
    return decorator
