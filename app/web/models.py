"""
ProfileScope Web Models
Database models for the ProfileScope web application
"""

import enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred

# Initialize SQLAlchemy
db = SQLAlchemy()

class TaskStatus(enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class Task(db.Model):
    """Task model for analysis tasks.

    This schema is used by:
    - `app/web/routes/api.py` and `app/web/routes/views.py`
    - the existing Alembic migration in `migrations/versions/*_initial_migration.py`
    - tests that expect progress + result_path fields.

    Keep this model in sync with API expectations.
    """

    # Match the existing Alembic migration table name.
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    profile_id = db.Column(db.String(255), nullable=False)

    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)

    # Progress tracking
    progress = db.Column(db.Integer, default=0)
    message = db.Column(db.String(255))

    # Result storage
    # Production-grade: persist results in DB (Postgres JSON/JSONB, SQLite JSON).
    # `result_path` is retained for backwards compatibility, but production should
    # prefer `result_data`.
    result_path = db.Column(db.String(255))
    # Large payload: defer loading by default so list endpoints stay fast.
    # Use JSONB on Postgres, JSON elsewhere.
    result_data = deferred(db.Column(JSONB().with_variant(db.JSON, "sqlite")))
    has_result = db.Column(db.Boolean, default=False, nullable=False)

    # Error handling
    error = db.Column(db.Text)

    # Duration tracking (seconds)
    duration = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Task {self.id}: {self.platform}/{self.profile_id} - {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "profile_id": self.profile_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result_path": self.result_path,
            "has_result": self.has_result,
            "error": self.error,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'

class AnalysisStatus(enum.Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Analysis(db.Model):
    """Analysis model for storing analysis results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    platform = db.Column(db.String(50), nullable=False)
    profile_id = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    analysis_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Analysis {self.id}: {self.platform}/{self.profile_id}>'