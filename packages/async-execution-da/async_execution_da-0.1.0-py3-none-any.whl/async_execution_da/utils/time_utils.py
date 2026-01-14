from datetime import datetime
from zoneinfo import ZoneInfo


def now_str() -> str:
    """
    Return New York timezone timestamp string, to millisecond precision.
    Example: "10-29 15:42:11.123"
    """
    ny_tz = ZoneInfo("America/New_York")
    return datetime.now(ny_tz).strftime("%m-%d %H:%M:%S.%f")[:-3]


def log(msg: str):
    """Print a log message with timestamp."""
    print(f"[{now_str()}] {msg}")
