"""
ProfileScope Desktop Views Package
"""

from .main_view import MainView
from .results_view import ResultsView
from .timeline_view import TimelineView
from .traits_view import TraitsView
from .writing_view import WritingView
from .auth_view import AuthView
from .predict_view import PredictView

__all__ = [
    "MainView",
    "ResultsView",
    "TimelineView",
    "TraitsView",
    "WritingView",
    "AuthView",
    "PredictView",
]
