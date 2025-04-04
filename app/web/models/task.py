# app/web/models/task.py
import datetime
from typing import Dict, List, Any, Optional

# In-memory storage for ongoing analyses
analysis_tasks = {}


class AnalysisTask:
    """Class to track analysis task status"""

    def __init__(self, task_id: str, platform: str, profile_id: str):
        self.task_id = task_id
        self.platform = platform
        self.profile_id = profile_id
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.message = "Waiting to start..."
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for API responses"""
        result = {
            "task_id": self.task_id,
            "platform": self.platform,
            "profile_id": self.profile_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
        }

        if self.start_time:
            result["start_time"] = self.start_time.isoformat()

        if self.end_time:
            result["end_time"] = self.end_time.isoformat()

        if self.error:
            result["error"] = self.error

        return result

    def start(self):
        """Mark task as started"""
        self.status = "running"
        self.start_time = datetime.datetime.now()
        self.message = "Analysis started"
        self.progress = 5

    def update_progress(self, progress: int, message: str):
        """Update progress information"""
        self.progress = progress
        self.message = message

    def complete(self, result: Dict[str, Any]):
        """Mark task as completed with result"""
        self.status = "completed"
        self.end_time = datetime.datetime.now()
        self.progress = 100
        self.message = "Analysis completed successfully"
        self.result = result

    def fail(self, error: str):
        """Mark task as failed with error"""
        self.status = "failed"
        self.end_time = datetime.datetime.now()
        self.message = "Analysis failed"
        self.error = error
