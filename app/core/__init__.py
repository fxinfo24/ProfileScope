"""
ProfileScope Core Module
Contains the main functionality for analyzing social media profiles
"""

__version__ = "1.0.0"

# Lazy imports - only import when actually used to avoid requiring heavy dependencies
# This allows the web app to start without ML/API packages
__all__ = [
    "SocialMediaAnalyzer",
    "DataCollector",
    "ContentAnalyzer",
    "ProfileAuthenticityAnalyzer",
    "PredictionEngine",
]

def __getattr__(name):
    """Lazy import core modules to avoid loading heavy dependencies at startup"""
    if name == "SocialMediaAnalyzer":
        from .analyzer import SocialMediaAnalyzer
        return SocialMediaAnalyzer
    elif name == "DataCollector":
        from .data_collector import DataCollector
        return DataCollector
    elif name == "ContentAnalyzer":
        from .content_analyzer import ContentAnalyzer
        return ContentAnalyzer
    elif name == "ProfileAuthenticityAnalyzer":
        from .authenticity import ProfileAuthenticityAnalyzer
        return ProfileAuthenticityAnalyzer
    elif name == "PredictionEngine":
        from .prediction import PredictionEngine
        return PredictionEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
