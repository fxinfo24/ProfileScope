# app/web/routes/api.py
"""
ProfileScope API Routes
Handles API endpoints for tasks and analysis results
"""
from flask import Blueprint, jsonify, request, current_app, send_file
from pathlib import Path
from datetime import datetime
import json
import threading
import logging

from app.core.analyzer import SocialMediaAnalyzer
from ..models import db, Task, TaskStatus

logger = logging.getLogger("api")

# Initialize analyzer
analyzer = SocialMediaAnalyzer()

api_bp = Blueprint("api", __name__)


def run_analysis(task_id: int, platform: str, profile_id: str):
    """Run analysis in background thread"""
    with current_app.app_context():
        task = Task.query.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        try:
            # Update task status
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            db.session.commit()

            # Run the actual analysis
            result = analyzer.analyze_profile(platform, profile_id)

            # Save result to file
            result_path = Path(current_app.config["RESULTS_FOLDER"]) / f"{task_id}.json"
            result_path.parent.mkdir(parents=True, exist_ok=True)

            with open(result_path, "w") as f:
                json.dump(result, f, indent=2)

            # Update task as complete
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result_path = str(result_path)
            db.session.commit()

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.session.commit()


@api_bp.route("/analyze", methods=["POST"])
def start_analysis():
    """Start a new profile analysis task"""
    data = request.get_json()

    if not data or "platform" not in data or "profile_id" not in data:
        return (
            jsonify({"error": "Missing required fields: platform and profile_id"}),
            400,
        )

    # Create new task
    task = Task(
        platform=data["platform"].lower(),
        profile_id=data["profile_id"],
        status=TaskStatus.PENDING,
    )

    db.session.add(task)
    db.session.commit()

    # Start analysis in background
    thread = threading.Thread(
        target=run_analysis, args=(task.id, task.platform, task.profile_id)
    )
    thread.daemon = True
    thread.start()

    return (jsonify({"message": "Analysis task created", "task": task.to_dict()}), 202)


@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get task status and details"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    """List all tasks with optional filtering"""
    # Get query parameters
    platform = request.args.get("platform")
    status = request.args.get("status")
    limit = request.args.get("limit", type=int, default=10)
    offset = request.args.get("offset", type=int, default=0)

    # Build query
    query = Task.query

    if platform:
        query = query.filter_by(platform=platform.lower())
    if status:
        try:
            task_status = TaskStatus(status.upper())
            query = query.filter_by(status=task_status)
        except ValueError:
            return jsonify({"error": f"Invalid status: {status}"}), 400

    # Get total count
    total = query.count()

    # Apply pagination
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify(
        {
            "tasks": [task.to_dict() for task in tasks],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )


@api_bp.route("/tasks/<int:task_id>/status", methods=["GET"])
def get_task_status(task_id):
    """Get task status only - for polling"""
    task = Task.query.get_or_404(task_id)
    return jsonify(
        {
            "id": task.id,
            "status": task.status.value,
            "progress": task.progress,
            "message": task.message,
            "error": task.error,
        }
    )


@api_bp.route("/tasks/<int:task_id>/cancel", methods=["POST"])
def cancel_task(task_id):
    """Cancel a pending or processing task"""
    task = Task.query.get_or_404(task_id)

    if task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
        msg = "Can only cancel pending or processing tasks"
        return jsonify({"error": msg}), 400

    task.status = TaskStatus.FAILED
    task.error_message = "Task cancelled by user"
    task.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Task cancelled", "task": task.to_dict()})


@api_bp.route("/tasks/<int:task_id>/results", methods=["GET"])
def get_results(task_id):
    """Get analysis results for a completed task"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.COMPLETED:
        msg = "Results only available for completed tasks"
        return jsonify({"error": msg}), 400

    if not task.result_path or not Path(task.result_path).exists():
        return jsonify({"error": "Result file not found"}), 404

    try:
        with open(task.result_path, "r") as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error reading results for task {task_id}: {e}")
        return jsonify({"error": "Error reading results file"}), 500


@api_bp.route("/tasks/<int:task_id>/download", methods=["GET"])
def download_results(task_id):
    """Download task results as a file"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.COMPLETED:
        msg = "Can only download results for completed tasks"
        return jsonify({"error": msg}), 400

    if not task.result_path or not Path(task.result_path).exists():
        return jsonify({"error": "Result file not found"}), 404

    return send_file(
        task.result_path,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"analysis_{task.platform}_{task.profile_id}.json",
    )


@api_bp.route("/stats/platform-distribution", methods=["GET"])
def platform_distribution():
    """Get platform distribution statistics"""
    platform_stats = (
        db.session.query(Task.platform, db.func.count(Task.id).label("count"))
        .group_by(Task.platform)
        .all()
    )

    return jsonify(
        [{"platform": platform, "count": count} for platform, count in platform_stats]
    )


@api_bp.route("/stats/completion-rate", methods=["GET"])
def completion_rate():
    """Get task completion rate statistics"""
    total = Task.query.count()
    completed = Task.query.filter_by(status=TaskStatus.COMPLETED).count()
    failed = Task.query.filter_by(status=TaskStatus.FAILED).count()

    return jsonify(
        {
            "total": total,
            "completed": completed,
            "failed": failed,
            "completion_rate": (completed / total if total > 0 else 0) * 100,
        }
    )
