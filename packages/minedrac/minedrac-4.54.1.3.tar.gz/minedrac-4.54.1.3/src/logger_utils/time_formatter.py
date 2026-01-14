import datetime


def format_date(date_str: str) -> str:
    """Convert ISO date string to YYYY-MM-dd-hh:mm."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))  # handle UTC 'Z' if present
        return dt.strftime("%Y-%m-%d-%H:%M")
    except ValueError:
        return ""
