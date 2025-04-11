"""
Custom template filters for the web interface
"""

from datetime import datetime
from flask import Flask
from app.web.models import TaskStatus


def register_filters(app: Flask):
    """Register custom filters with Flask app"""

    @app.template_filter("datetime")
    def format_datetime(value):
        """Format a datetime object to a readable string"""
        if not value:
            return ""
        return value.strftime("%b %d, %Y %H:%M")

    @app.template_filter("duration")
    def format_duration(seconds):
        """Format duration in seconds to a readable string"""
        if not seconds:
            return "-"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{remaining_seconds}s")

        return " ".join(parts)

    @app.template_filter("status_badge")
    def status_badge_class(status):
        """Convert task status to appropriate Bootstrap badge class"""
        if isinstance(status, str):
            status = status.lower()
        elif isinstance(status, TaskStatus):
            status = status.value

        badge_map = {
            "pending": "secondary",
            "processing": "primary",
            "completed": "success",
            "failed": "danger",
        }

        return badge_map.get(status, "secondary")

    @app.template_filter("status_badge_class")
    def get_status_badge_class(status):
        """Get full badge class based on status"""
        return f"bg-{status_badge_class(status)}"

    @app.template_filter("risk_color")
    def risk_color(score):
        """Return color class based on risk score (0-1)"""
        if score < 0.3:
            return "danger"
        elif score < 0.7:
            return "warning"
        else:
            return "success"
