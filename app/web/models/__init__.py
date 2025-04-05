"""
ProfileScope Web Models Package
"""

from .. import db
from .task import Task, TaskStatus

__all__ = ["Task", "TaskStatus", "db"]
