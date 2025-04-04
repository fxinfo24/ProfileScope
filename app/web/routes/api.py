# app/web/routes/api.py
from flask import request, jsonify, send_file
from app.web import app
from app.core.analyzer import SocialMediaAnalyzer
from app.web.models.task import AnalysisTask, analysis_tasks
import os
import threading
import datetime
import uuid
import time
import json
import logging

logger = logging.getLogger("api")

# Initialize analyzer
analyzer = SocialMediaAnalyzer()


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


@app.route("/api/status", methods=["GET"])
def api_status():
    """API endpoint to check service status"""
    return jsonify(
        {
            "status": "online",
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
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
