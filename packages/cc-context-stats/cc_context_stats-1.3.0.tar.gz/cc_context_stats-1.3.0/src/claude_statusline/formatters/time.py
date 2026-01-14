"""Time and duration formatting utilities."""

from __future__ import annotations

import time
from datetime import datetime


def format_timestamp(ts: int) -> str:
    """Format Unix timestamp as time string.

    Args:
        ts: Unix timestamp (seconds since epoch)

    Returns:
        Formatted time string like "14:30"
    """
    try:
        return datetime.fromtimestamp(ts).strftime("%H:%M")
    except (ValueError, OSError):
        return str(ts)


def format_duration(seconds: int) -> str:
    """Format duration in seconds as human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2h 30m" or "45m" or "30s"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def get_current_timestamp() -> int:
    """Get current Unix timestamp.

    Returns:
        Current time as Unix timestamp
    """
    return int(time.time())
