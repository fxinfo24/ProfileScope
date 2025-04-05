# app/web/routes/api.py
"""
ProfileScope API Routes
Handles API endpoints for tasks and analysis results
"""

from flask import Blueprint, jsonify, request, current_app, send_file
from pathlib import Path
from datetime import datetime
from app.web import app
from app.core.analyzer import SocialMediaAnalyzer
from app.web.models.task import AnalysisTask, analysis_tasks
import os
import threading
import uuid
import time
import json
import logging

from ..models import db, Task, TaskStatus

logger = logging.getLogger("api")

# Initialize analyzer
analyzer = SocialMediaAnalyzer()

api_bp = Blueprint("api", __name__)


def run_analysis(task_id: str, platform: str, profile_id: str):
    """Run analysis in background thread"""
    task = analysis_tasks[task_id]

    try:
        # Start the task
        task.start()

        # Simulate or track real progress steps
        task.update_progress(10, "Collecting profile data...")
        time.sleep(1)  # In real app, this would be actual work

        task.update_progress(30, "Analyzing content...")
        time.sleep(1.5)

        task.update_progress(50, "Evaluating authenticity...")
        time.sleep(1)

        task.update_progress(70, "Generating predictions...")
        time.sleep(1)

        task.update_progress(90, "Finalizing analysis...")

        # Run the actual analysis
        result = analyzer.analyze_profile(platform, profile_id)

        # Save result to file
        result_path = os.path.join(app.config["RESULTS_FOLDER"], f"{task_id}.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)

        # Mark as complete
        task.complete(result)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        task.fail(str(e))


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
    task = Task(platform=data["platform"], profile_id=data["profile_id"])

    db.session.add(task)
    db.session.commit()

    # Return task details
    return jsonify({"message": "Analysis task created", "task": task.to_dict()}), 202


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
            task_status = TaskStatus(status.lower())
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


@api_bp.route("/tasks/<int:task_id>/cancel", methods=["POST"])
def cancel_task(task_id):
    """Cancel a pending task"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.PENDING:
        return jsonify({"error": "Only pending tasks can be cancelled"}), 400

    task.fail("Task cancelled by user")
    db.session.commit()

    return jsonify({"message": "Task cancelled", "task": task.to_dict()})


@api_bp.route("/tasks/<int:task_id>/results", methods=["GET"])
def get_results(task_id):
    """Get analysis results for a completed task"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.COMPLETED:
        return jsonify({"error": "Results only available for completed tasks"}), 400

    if not task.result_path or not Path(task.result_path).exists():
        return jsonify({"error": "Result file not found"}), 404

    try:
        with open(task.result_path, "r") as f:
            results = f.read()
        return results, 200, {"Content-Type": "application/json"}
    except Exception as e:
        return jsonify({"error": f"Error reading results: {str(e)}"}), 500


@api_bp.route("/platforms", methods=["GET"])
def list_platforms():
    """List supported social media platforms"""
    return jsonify(
        {
            "platforms": [
                {"id": "twitter", "name": "Twitter/X", "enabled": True},
                {"id": "facebook", "name": "Facebook", "enabled": True},
            ]
        }
    )


@app.route("/api/status", methods=["GET"])
def api_status():
    """API endpoint to check service status"""
    return jsonify(
        {
            "status": "online",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """API endpoint to start analysis"""
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        if "platform" not in data or "profile_id" not in data:
            return (
                jsonify({"error": "Missing required fields: platform, profile_id"}),
                400,
            )

        platform = data["platform"].lower()
        profile_id = data["profile_id"]

        # Validate platform
        if platform not in ["twitter", "facebook"]:
            return jsonify({"error": f"Unsupported platform: {platform}"}), 400

        # Create task ID
        task_id = str(uuid.uuid4())

        # Create and store task
        task = AnalysisTask(task_id, platform, profile_id)
        analysis_tasks[task_id] = task

        # Start analysis in background
        thread = threading.Thread(
            target=run_analysis, args=(task_id, platform, profile_id)
        )
        thread.daemon = True
        thread.start()

        # Return task info
        return jsonify(
            {
                "task_id": task_id,
                "status": "pending",
                "message": "Analysis task created",
            }
        )

    except Exception as e:
        logger.error(f"Error creating analysis task: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error creating analysis task: {str(e)}"}), 500


@app.route("/api/tasks/<task_id>", methods=["GET"])
def api_task_status(task_id):
    """API endpoint to check task status"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404

    task = analysis_tasks[task_id]
    return jsonify(task.to_dict())


@app.route("/api/tasks/<task_id>/result", methods=["GET"])
def api_task_result(task_id):
    """API endpoint to get task result"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404

    task = analysis_tasks[task_id]

    if task.status != "completed":
        return jsonify({"error": "Task not completed", "status": task.status}), 400

    # Get result from memory or file
    if task.result:
        return jsonify(task.result)
    else:
        # Try to load from file
        result_path = os.path.join(app.config["RESULTS_FOLDER"], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Result not found"}), 404


@app.route("/api/tasks/<task_id>/download", methods=["GET"])
def api_task_download(task_id):
    """API endpoint to download result as file"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404

    task = analysis_tasks[task_id]

    if task.status != "completed":
        return jsonify({"error": "Task not completed", "status": task.status}), 400

    # Check if result file exists
    result_path = os.path.join(app.config["RESULTS_FOLDER"], f"{task_id}.json")
    if not os.path.exists(result_path):
        return jsonify({"error": "Result file not found"}), 404

    return send_file(
        result_path,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"analysis_{task.platform}_{task.profile_id}.json",
    )


@api_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get task status and progress"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@api_bp.route("/api/tasks/<int:task_id>/cancel", methods=["POST"])
def cancel_task(task_id):
    """Cancel a pending or processing task"""
    task = Task.query.get_or_404(task_id)

    if task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
        return jsonify({"error": "Can only cancel pending or processing tasks"}), 400

    task.fail("Task cancelled by user")
    db.session.commit()

    return jsonify({"status": "cancelled"})


@api_bp.route("/api/tasks/<int:task_id>/results", methods=["GET"])
def get_results(task_id):
    """Get analysis results for a completed task"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.COMPLETED:
        return jsonify({"error": "Results only available for completed tasks"}), 400

    if not task.result_path or not Path(task.result_path).exists():
        return jsonify({"error": "Result file not found"}), 404

    try:
        with open(task.result_path, "r") as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error reading results for task {task_id}: {e}")
        return jsonify({"error": "Error reading results file"}), 500


@api_bp.route("/api/tasks/<int:task_id>/logs", methods=["GET"])
def get_task_logs(task_id):
    """Get task processing logs"""
    task = Task.query.get_or_404(task_id)

    # Get log entries from database or file
    logs = []  # TODO: Implement log retrieval

    return jsonify({"task_id": task_id, "logs": logs})


@api_bp.route("/api/stats/platform-distribution", methods=["GET"])
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


@api_bp.route("/api/stats/completion-rate", methods=["GET"])
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


@api_bp.route("/api/stats/duration-trends", methods=["GET"])
def duration_trends():
    """Get analysis duration trends"""
    # Get average duration by day for the last 30 days
    duration_stats = (
        db.session.query(
            db.func.date(Task.created_at).label("date"),
            db.func.avg(Task.duration).label("avg_duration"),
        )
        .filter(Task.status == TaskStatus.COMPLETED)
        .group_by(db.func.date(Task.created_at))
        .order_by(db.func.date(Task.created_at).desc())
        .limit(30)
        .all()
    )

    return jsonify(
        [
            {
                "date": date.isoformat(),
                "average_duration": float(avg_duration) if avg_duration else 0,
            }
            for date, avg_duration in duration_stats
        ]
    )


@api_bp.route("/api/export/results/<int:task_id>", methods=["GET"])
def export_results(task_id):
    """Export analysis results in specified format"""
    task = Task.query.get_or_404(task_id)
    export_format = request.args.get("format", "json")

    if task.status != TaskStatus.COMPLETED:
        return jsonify({"error": "Can only export results for completed tasks"}), 400

    try:
        with open(task.result_path, "r") as f:
            results = json.load(f)

        if export_format == "json":
            return jsonify(results)
        else:
            return (
                jsonify({"error": f"Unsupported export format: {export_format}"}),
                400,
            )

    except Exception as e:
        current_app.logger.error(f"Error exporting results for task {task_id}: {e}")
        return jsonify({"error": "Error exporting results"}), 500
