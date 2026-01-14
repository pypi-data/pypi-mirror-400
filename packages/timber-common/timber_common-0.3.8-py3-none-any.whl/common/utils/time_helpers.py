from datetime import datetime, timedelta, timezone
def current_utc(): return datetime.now(timezone.utc)
def utc_plus_5min(): return datetime.now(timezone.utc) + timedelta(minutes=5)
def utc_plus_1hour() -> datetime:
    """Returns the current timezone-aware timezone.utc datetime plus 1 hour."""
    return datetime.now(timezone.utc) + timedelta(hours=1)