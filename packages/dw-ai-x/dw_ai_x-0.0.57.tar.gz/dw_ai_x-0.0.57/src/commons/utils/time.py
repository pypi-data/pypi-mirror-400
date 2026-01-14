"""
Time utilities.
"""

from datetime import datetime, timezone


def get_current_time() -> datetime:
    """
    Returns the current time in UTC.
    """
    return datetime.now(timezone.utc)


def convert_to_utc(time: datetime) -> datetime:
    """
    Converts a time to UTC.
    """
    return time.astimezone(timezone.utc)
