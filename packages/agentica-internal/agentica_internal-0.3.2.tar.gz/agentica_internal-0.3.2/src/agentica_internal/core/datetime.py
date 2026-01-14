from datetime import datetime, timezone


def time_now_utc() -> str:
    """current UTC time in ISO format"""
    return datetime.now(timezone.utc).isoformat()
