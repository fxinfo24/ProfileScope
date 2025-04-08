"""
Custom filters for Jinja2 templates
"""

from datetime import datetime


def format_datetime(value):
    """Format datetime to readable string"""
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value.strftime("%b %d, %Y, %H:%M")


def format_duration(seconds):
    """Format seconds into human-readable duration"""
    if not seconds:
        return "-"

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def status_badge(status):
    """Convert task status to Bootstrap badge color"""
    badges = {
        "pending": "warning",
        "processing": "primary",
        "completed": "success",
        "failed": "danger",
    }
    return badges.get(status, "secondary")


def status_badge_class(status_enum):
    """Convert task status enum to Bootstrap badge class"""
    if hasattr(status_enum, "value"):
        status = status_enum.value
    else:
        status = str(status_enum).lower()

    return f"bg-{status_badge(status)}"


def register_filters(app):
    """Register custom filters with the Flask app"""
    app.jinja_env.filters["datetime"] = format_datetime
    app.jinja_env.filters["duration"] = format_duration
    app.jinja_env.filters["status_badge"] = status_badge
    app.jinja_env.filters["status_badge_class"] = status_badge_class
