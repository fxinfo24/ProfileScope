"""
Template filters for formatting data in templates
"""

from datetime import datetime
from typing import Optional, Union


def datetime_filter(value: Optional[Union[str, datetime]]) -> str:
    """Format datetime to readable string"""
    if not value:
        return "-"

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value

    return value.strftime("%b %d, %Y %I:%M %p")


def duration_filter(seconds: Optional[float]) -> str:
    """Format duration in seconds to human readable string"""
    if not seconds:
        return "-"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if remaining_seconds > 0 or not parts:
        parts.append(f"{remaining_seconds}s")

    return " ".join(parts)


def filesize_filter(size: Optional[int]) -> str:
    """Format file size in bytes to human readable string"""
    if not size:
        return "-"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def percentage_filter(value: Optional[float]) -> str:
    """Format float as percentage"""
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def risk_color(level: str) -> str:
    """Get Bootstrap color class for risk level"""
    colors = {
        "low": "success",
        "medium": "warning",
        "high": "danger",
        "unknown": "secondary",
    }
    return colors.get(level.lower(), "secondary")


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + suffix


def status_badge_class(status: str) -> str:
    """Get Bootstrap badge class for task status"""
    classes = {
        "pending": "warning",
        "processing": "info",
        "completed": "success",
        "failed": "danger",
    }
    return f"badge bg-{classes.get(status.lower(), 'secondary')}"
