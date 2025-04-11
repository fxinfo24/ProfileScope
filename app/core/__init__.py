"""
ProfileScope Core Module
Contains the main functionality for analyzing social media profiles
"""

from .analyzer import SocialMediaAnalyzer
from .data_collector import DataCollector
from .content_analyzer import ContentAnalyzer
from .authenticity import ProfileAuthenticityAnalyzer
from .prediction import PredictionEngine

__version__ = "1.0.0"

__all__ = [
    "SocialMediaAnalyzer",
    "DataCollector",
    "ContentAnalyzer",
    "ProfileAuthenticityAnalyzer",
    "PredictionEngine",
]
