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
import os
import logging

from app.core.analyzer import SocialMediaAnalyzer
from ..models import db, Task, TaskStatus

logger = logging.getLogger("api")

# Initialize analyzer
analyzer = SocialMediaAnalyzer()

api_bp = Blueprint("api", __name__)


def run_analysis(task_id: int, platform: str, profile_id: str, app=None, mode: str = "deep"):
    """Run analysis in background thread
    
    Args:
        task_id: ID of the task to process
        platform: Social media platform
        profile_id: Profile identifier
        app: Flask app instance (required for thread context)
    """
    if app is None:
        app = current_app._get_current_object()
    
    with app.app_context():
        # Force new database connection for this thread
        # SQLAlchemy connections are not thread-safe
        db.session.remove()  # Remove any existing session
        
        task = Task.query.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        try:
            # Update task status
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            task.progress = 10
            task.message = "Processing"
            db.session.commit()

            # Run the actual analysis
            result = analyzer.analyze_profile(platform, profile_id, mode=mode)

            # Persist results in DB (production-grade)
            # task.result_data = result # Column missing in SQLite
            # task.has_result = True

            # Optional: also write a file in development environments
            result_path = Path(current_app.config["RESULTS_FOLDER"]) / f"{task_id}.json"
            try:
                result_path.parent.mkdir(parents=True, exist_ok=True)
                with open(result_path, "w") as f:
                    json.dump(result, f, indent=2)
                task.result_path = str(result_path)
            except Exception:
                # File persistence is best-effort; DB persistence is canonical
                task.result_path = None

            # Update task as complete
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress = 100
            task.message = "Completed"
            if task.started_at:
                task.duration = (task.completed_at - task.started_at).total_seconds()
            db.session.commit()

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            if task.started_at:
                task.duration = (task.completed_at - task.started_at).total_seconds()
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

    # Create new task (Task.__init__ only accepts platform and profile_id)
    task = Task(
        platform=data["platform"].lower(),
        profile_id=data["profile_id"]
    )
    # Status is set to PENDING by default in __init__

    db.session.add(task)
    db.session.commit()

    # Start analysis
    # FIXED: Use threading by default for Railway single-service deployment.
    # Celery requires a separate worker service which adds complexity and cost.
    # Threading is sufficient for current scale and works immediately.
    # 
    # To enable Celery in future: set FORCE_CELERY=true environment variable
    # and deploy a separate Railway worker service.
    force_celery = os.getenv("FORCE_CELERY", "").lower() == "true"
    redis_url = os.getenv("REDIS_URL")
    task_started = False
    
    if force_celery and redis_url:
        logger.info(f"FORCE_CELERY enabled, attempting Celery enqueue for task {task.id}")
        try:
            from app.core.tasks import run_task_analysis
            run_task_analysis.delay(task.id)
            task_started = True
            logger.info(f"Task {task.id} enqueued to Celery successfully")
        except Exception as e:
            logger.error(f"Failed to enqueue Celery task {task.id}: {e}", exc_info=True)
            logger.info(f"Falling back to threading for task {task.id}")
    
    if not task_started:
        # Use threading (default for Railway deployment without worker service)
        logger.info(f"Starting task {task.id} in background thread")
        try:
            # Pass app instance to thread for context
            app_instance = current_app._get_current_object()
            mode = data.get("mode", "deep")
            thread = threading.Thread(
                target=run_analysis, 
                args=(task.id, task.platform, task.profile_id, app_instance, mode)
            )
            thread.daemon = True
            thread.start()
            task_started = True
            logger.info(f"Task {task.id} started in background thread successfully")
        except Exception as e:
            logger.error(f"Failed to start background thread for task {task.id}: {e}", exc_info=True)
            # Update task as failed
            task.status = TaskStatus.FAILED
            task.error = f"Failed to start analysis: {str(e)}"
            db.session.commit()
            return (jsonify({
                "error": "Failed to start analysis task",
                "details": str(e),
                "task": task.to_dict()
            }), 500)

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
            # TaskStatus values are lowercase ("pending", "processing", ...)
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
    task.error = "Task cancelled by user"
    task.completed_at = datetime.utcnow()
    if task.started_at:
        task.duration = (task.completed_at - task.started_at).total_seconds()
    db.session.commit()

    return jsonify({"message": "Task cancelled", "task": task.to_dict()})


@api_bp.route("/tasks/<int:task_id>/retry", methods=["POST"])
def retry_task(task_id):
    """Retry a stuck or failed task using threading (bypass Celery)"""
    task = Task.query.get_or_404(task_id)

    # Only allow retrying pending, failed, or stuck processing tasks
    if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED, TaskStatus.PROCESSING]:
        msg = "Can only retry pending, failed, or processing tasks"
        return jsonify({"error": msg}), 400

    logger.info(f"Retrying task {task.id} (status: {task.status.value})")
    
    # Reset task to pending state
    task.status = TaskStatus.PENDING
    task.error = None
    task.started_at = None
    task.completed_at = None
    task.progress = 0
    task.message = "Retrying"
    db.session.commit()

    # Start task using threading (force bypass Celery)
    try:
        # Pass app instance to thread for context
        app_instance = current_app._get_current_object()
        thread = threading.Thread(
            target=run_analysis, 
            args=(task.id, task.platform, task.profile_id, app_instance)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Task {task.id} retry started in background thread")
        return jsonify({"message": "Task retry started", "task": task.to_dict()}), 200
    except Exception as e:
        logger.error(f"Failed to retry task {task.id}: {e}", exc_info=True)
        task.status = TaskStatus.FAILED
        task.error = f"Failed to retry: {str(e)}"
        db.session.commit()
        return jsonify({"error": "Failed to retry task", "details": str(e)}), 500


@api_bp.route("/tasks/<int:task_id>/results", methods=["GET"])
def get_results(task_id):
    """Get analysis results for a completed task"""
    task = Task.query.get_or_404(task_id)

    if task.status != TaskStatus.COMPLETED:
        msg = "Results only available for completed tasks"
        return jsonify({"error": msg}), 400

    # Canonical source: DB
    # Canonical source: DB - Only check if attribute exists (compatibility)
    if hasattr(task, 'result_data') and task.result_data is not None:
        return jsonify(task.result_data)

    # Backward-compatible fallback: file
    if task.result_path and Path(task.result_path).exists():
        try:
            with open(task.result_path, "r") as f:
                results = json.load(f)
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error reading results for task {task_id}: {e}")

    # If no data found, return empty structure to prevent frontend errors
    return jsonify({
        "profile_info": {
            "username": task.profile_id,
            "followers": 0,
            "following": 0, 
            "posts": 0
        },
        "sentiment": {
            "overall": "neutral",
            "positive": 0,
            "neutral": 100,
            "negative": 0
        },
        "content_analysis": {},
        "authenticity": {},
        "predictions": {},
        "metadata": {
            "error": "No result data available"
        }
    })


@api_bp.route("/tasks/<int:task_id>/download", methods=["GET"])
def download_results(task_id):
    """Download task results as a file (JSON or HTML Dossier)"""
    task = Task.query.get_or_404(task_id)
    output_format = request.args.get('format', 'json').lower()

    if task.status != TaskStatus.COMPLETED:
        msg = "Can only download results for completed tasks"
        return jsonify({"error": msg}), 400

    # Get data (DB or file)
    data = None
    # if hasattr(task, 'result_data'): data = task.result_data
    
    if data is None and task.result_path and Path(task.result_path).exists():
        with open(task.result_path, "r") as f:
            data = json.load(f)

    if not data:
        print("DEBUG: Result data is empty/None")
        return jsonify({"error": "Results not found"}), 404
    
    print(f"DEBUG: Result data type: {type(data)}")
    # print(f"DEBUG: Result data keys: {data.keys() if isinstance(data, dict) else 'Not Dict'}")

    # HTML Dossier Export
    # HTML Dossier Export
    if output_format in ['html', 'pdf']:
        try:
            from app.core.report_generator import DossierReportGenerator
            generator = DossierReportGenerator()
            # Pass dictionary directly
            html_content = generator.generate_html_report(data)
            
            return current_app.response_class(
                html_content,
                mimetype="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=dossier_{task.profile_id}.html"
                }
            )
        except Exception as e:
            print(f"DEBUG: HTML generation error: {e}")
            return jsonify({"error": f"Report generation failed: {e}", "details": str(e)}), 500

    # Default JSON Export
    try:
        payload = json.dumps(data, indent=2, default=str)
    except Exception as e:
        print(f"DEBUG: JSON serialization error: {e}")
        return jsonify({"error": f"Serialization error: {e}"}), 500

    return current_app.response_class(
        payload,
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{task.platform}_{task.profile_id}.json"
        },
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


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker/Kubernetes"""
    try:
        # Check database connection
        db.session.execute(db.text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return jsonify({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@api_bp.route("/platforms", methods=["GET"])
def list_platforms():
    """List all supported social media platforms"""
    # All platforms supported by ScrapeCreators (except Truth Social)
    platforms = [
        {"id": "twitter", "name": "Twitter/X", "category": "social"},
        {"id": "instagram", "name": "Instagram", "category": "social"},
        {"id": "tiktok", "name": "TikTok", "category": "social"},
        {"id": "youtube", "name": "YouTube", "category": "video"},
        {"id": "linkedin", "name": "LinkedIn", "category": "professional"},
        {"id": "facebook", "name": "Facebook", "category": "social"},
        {"id": "reddit", "name": "Reddit", "category": "social"},
        {"id": "pinterest", "name": "Pinterest", "category": "social"},
        {"id": "snapchat", "name": "Snapchat", "category": "social"},
        {"id": "threads", "name": "Threads", "category": "social"},
        {"id": "bluesky", "name": "Bluesky", "category": "social"},
        {"id": "twitch", "name": "Twitch", "category": "streaming"},
        {"id": "kick", "name": "Kick", "category": "streaming"},
        {"id": "github", "name": "GitHub", "category": "developer"},
        {"id": "linktree", "name": "Linktree", "category": "links"},
        {"id": "komi", "name": "Komi", "category": "links"},
        {"id": "pillar", "name": "Pillar", "category": "links"},
        {"id": "linkbio", "name": "Linkbio", "category": "links"},
        {"id": "google", "name": "Google", "category": "search"},
        {"id": "tiktok_shop", "name": "TikTok Shop", "category": "commerce"},
        {"id": "amazon_shop", "name": "Amazon Shop", "category": "commerce"},
    ]
    
    return jsonify({
        "platforms": platforms,
        "total": len(platforms),
        "categories": list(set(p["category"] for p in platforms))
    })
