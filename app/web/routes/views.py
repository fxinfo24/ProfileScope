# app/web/routes/views.py
from flask import render_template, redirect, url_for, request
from app.web import app
from app.web.models.task import analysis_tasks


@app.route("/")
def home():
    """Homepage with analysis form"""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def web_analyze():
    """Web form handler to start analysis"""
    platform = request.form.get("platform", "").lower()
    profile_id = request.form.get("profile_id", "")

    # Validate inputs
    if not platform or not profile_id:
        return render_template(
            "index.html", error="Please provide both platform and profile ID"
        )

    if platform not in ["twitter", "facebook"]:
        return render_template("index.html", error=f"Unsupported platform: {platform}")

    # Create analysis task (same as API)
    task_id = str(uuid.uuid4())
    task = AnalysisTask(task_id, platform, profile_id)
    analysis_tasks[task_id] = task

    # Start analysis in background
    thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
    thread.daemon = True
    thread.start()

    # Redirect to monitoring page
    return redirect(url_for("task_monitor", task_id=task_id))


@app.route("/tasks/<task_id>")
def task_monitor(task_id):
    """Page to monitor task progress"""
    if task_id not in analysis_tasks:
        return render_template("error.html", error="Task not found")

    task = analysis_tasks[task_id]
    return render_template("task.html", task=task)


@app.route("/results/<task_id>")
def view_result(task_id):
    """Page to view analysis results"""
    if task_id not in analysis_tasks:
        return render_template("error.html", error="Task not found")

    task = analysis_tasks[task_id]

    if task.status != "completed":
        return redirect(url_for("task_monitor", task_id=task_id))

    # Load result if not in memory
    if not task.result:
        result_path = os.path.join(app.config["RESULTS_FOLDER"], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                task.result = json.load(f)
        else:
            return render_template("error.html", error="Result not found")

    return render_template("result.html", task=task, result=task.result)


@app.route("/dashboard")
def dashboard():
    """Admin dashboard to see all tasks"""
    tasks = {tid: task.to_dict() for tid, task in analysis_tasks.items()}
    return render_template("dashboard.html", tasks=tasks)
