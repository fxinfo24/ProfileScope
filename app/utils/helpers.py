"""
Vanta: Utility Helper Functions
Common utility functions used across the application
"""

from datetime import datetime
import re
from typing import List, Optional
from urllib.parse import urlparse


def format_date(date_str: Optional[str], fmt: str = "%Y-%m-%d") -> str:
    """
    Format date string to specified format

    Args:
        date_str: Date string to format
        fmt: Output format (default: YYYY-MM-DD)

    Returns:
        Formatted date string
    """
    if not date_str:
        return ""

    try:
        # Try parsing common date formats
        for fmt_in in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                date_obj = datetime.strptime(date_str, fmt_in)
                return date_obj.strftime(fmt)
            except ValueError:
                continue
        return date_str  # Return original if parsing fails
    except Exception:
        return date_str


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text

    Args:
        text: Text to extract URLs from

    Returns:
        List of extracted URLs
    """
    # URL regex pattern
    url_pattern = (
        r"http[s]?://"  # http:// or https://
        r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|"  # allowed characters
        r"(?:%[0-9a-fA-F][0-9a-fA-F]))+"  # percent-encoded characters
    )

    # Find all URLs in text
    urls = re.findall(url_pattern, text)

    # Validate and clean URLs
    valid_urls = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                valid_urls.append(url)
        except Exception:
            continue

    return valid_urls


def clean_text(text: str) -> str:
    """
    Clean and normalize text

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove control characters
    text = "".join(char for char in text if ord(char) >= 32 or char == "\n")

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove multiple consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
