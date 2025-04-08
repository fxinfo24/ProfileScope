"""
Web application models
Database models for the ProfileScope web interface
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .task import Task, TaskStatus

__all__ = ["Task", "TaskStatus", "db"]
