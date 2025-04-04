# Destination in Project Structure app/web/app.py

# SocialInsight: Web API and Interface
# A web-based interface for the Social Media Profile Analyzer

from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import os
import json
import threading
import datetime
import time
import uuid
import logging
from typing import Dict, List, Any, Optional

# Import the analyzer core
from social_media_analyzer import SocialMediaAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='socialinsight_web.log'
)
logger = logging.getLogger('SocialInsightWeb')

# Initialize Flask app
app = Flask(__name__, 
          static_url_path='/static',
          template_folder='templates')

# Configure app
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize analyzer in global context
analyzer = SocialMediaAnalyzer()

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
            "message": self.message
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
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Mark as complete
        task.complete(result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        task.fail(str(e))


# API Routes
@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint to check service status"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint to start analysis"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if "platform" not in data or "profile_id" not in data:
            return jsonify({"error": "Missing required fields: platform, profile_id"}), 400
            
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
        thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
        thread.daemon = True
        thread.start()
        
        # Return task info
        return jsonify({
            "task_id": task_id,
            "status": "pending",
            "message": "Analysis task created"
        })
        
    except Exception as e:
        logger.error(f"Error creating analysis task: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error creating analysis task: {str(e)}"}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """API endpoint to check task status"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>/result', methods=['GET'])
def api_task_result(task_id):
    """API endpoint to get task result"""
    if task_id not in analysis_tasks:
        return jsonify(
            
# v2

@app.route('/api/tasks/<task_id>/result', methods=['GET'])
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
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Result not found"}), 404

@app.route('/api/tasks/<task_id>/download', methods=['GET'])
def api_task_download(task_id):
    """API endpoint to download result as file"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    
    if task.status != "completed":
        return jsonify({"error": "Task not completed", "status": task.status}), 400
    
    # Check if result file exists
    result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
    if not os.path.exists(result_path):
        return jsonify({"error": "Result file not found"}), 404
    
    return send_file(
        result_path,
        mimetype='application/json',
        as_attachment=True,
        download_name=f"analysis_{task.platform}_{task.profile_id}.json"
    )


# Web Interface Routes
@app.route('/')
def home():
    """Homepage with analysis form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def web_analyze():
    """Web form handler to start analysis"""
    platform = request.form.get('platform', '').lower()
    profile_id = request.form.get('profile_id', '')
    
    # Validate inputs
    if not platform or not profile_id:
        return render_template('index.html', error="Please provide both platform and profile ID")
    
    if platform not in ["twitter", "facebook"]:
        return render_template('index.html', error=f"Unsupported platform: {platform}")
    
    # Create analysis task (same as API)
    task_id = str(uuid.uuid4())
    task = AnalysisTask(task_id, platform, profile_id)
    analysis_tasks[task_id] = task
    
    # Start analysis in background
    thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
    thread.daemon = True
    thread.start()
    
    # Redirect to monitoring page
    return redirect(url_for('task_monitor', task_id=task_id))

@app.route('/tasks/<task_id>')
def task_monitor(task_id):
    """Page to monitor task progress"""
    if task_id not in analysis_tasks:
        return render_template('error.html', error="Task not found")
    
    task = analysis_tasks[task_id]
    return render_template('task.html', task=task)

@app.route('/results/<task_id>')
def view_result(task_id):
    """Page to view analysis results"""
    if task_id not in analysis_tasks:
        return render_template('error.html', error="Task not found")
    
    task = analysis_tasks[task_id]
    
    if task.status != "completed":
        return redirect(url_for('task_monitor', task_id=task_id))
    
    # Load result if not in memory
    if not task.result:
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                task.result = json.load(f)
        else:
            return render_template('error.html', error="Result not found")
    
    return render_template('result.html', task=task, result=task.result)

@app.route('/dashboard')
def dashboard():
    """Admin dashboard to see all tasks"""
    tasks = {tid: task.to_dict() for tid, task in analysis_tasks.items()}
    return render_template('dashboard.html', tasks=tasks)


# HTML Templates (would be in separate files in templates directory)
# For brevity, including them as string templates

html_templates = {
    'index.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialInsight - Social Media Profile Analyzer</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="card-title mb-0">Analyze Social Media Profile</h3>
                    </div>
                    <div class="card-body">
                        {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                        {% endif %}
                        
                        <form action="/analyze" method="post">
                            <div class="mb-3">
                                <label for="platform" class="form-label">Social Media Platform</label>
                                <select class="form-select" id="platform" name="platform" required>
                                    <option value="" selected disabled>Select a platform</option>
                                    <option value="twitter">Twitter / X</option>
                                    <option value="facebook">Facebook</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="profile_id" class="form-label">Profile ID / Username</label>
                                <input type="text" class="form-control" id="profile_id" name="profile_id" 
                                       placeholder="Enter profile username or ID" required>
                                <div class="form-text">Enter the username or profile ID you want to analyze.</div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Collection Method</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_api" value="api" checked>
                                    <label class="form-check-label" for="method_api">API Access (Recommended)</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_web" value="web">
                                    <label class="form-check-label" for="method_web">Web Scraping</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_manual" value="manual">
                                    <label class="form-check-label" for="method_manual">Manual Input</label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Analysis Options</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_sentiment" id="include_sentiment" value="true" checked>
                                    <label class="form-check-label" for="include_sentiment">Include sentiment analysis</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_authenticity" id="include_authenticity" value="true" checked>
                                    <label class="form-check-label" for="include_authenticity">Include authenticity analysis</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_predictions" id="include_predictions" value="true" checked>
                                    <label class="form-check-label" for="include_predictions">Include predictions</label>
                                </div>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary">Start Analysis</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h4 class="mb-0">About SocialInsight</h4>
                    </div>
                    <div class="card-body">
                        <p>SocialInsight is an open-source tool designed to analyze publicly available social media profiles
                        and generate insights about personality traits, interests, writing style, and more.</p>
                        
                        <p><strong>Key Features:</strong></p>
                        <ul>
                            <li>Collection of public profile data (posts, images, links)</li>
                            <li>Personality trait analysis based on content</li>
                            <li>Interest and preference identification</li>
                            <li>Timeline generation and visualization</li>
                            <li>Writing style analysis</li>
                            <li>Authenticity evaluation and fake profile detection</li>
                            <li>Predictive analysis based on patterns</li>
                        </ul>
                        
                        <div class="alert alert-info mt-3">
                            <strong>Privacy Notice:</strong> SocialInsight only analyzes publicly available information.
                            No private data is accessed or stored without explicit permission.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>
    """,
    
    'task.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis in Progress - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="card-title mb-0">Analysis in Progress</h3>
                    </div>
                    <div class="card-body text-center p-5">
                        {% if task.status == "completed" %}
                            <div class="mb-4">
                                <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="mb-3">Analysis Complete!</h4>
                            <p class="mb-4">The analysis of {{ task.platform }} profile "{{ task.profile_id }}" has been completed successfully.</p>
                            <a href="/results/{{ task.task_id }}" class="btn btn-primary btn-lg">View Results</a>
                            
                        {% elif task.status == "failed" %}
                            <div class="mb-4">
                                <i class="bi bi-x-circle-fill text-danger" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="mb-3">Analysis Failed</h4>
                            <p class="text-danger mb-4">{{ task.error }}</p>
                            <a href="/" class="btn btn-primary btn-lg">Try Again</a>
                            
                        {% else %}
                            <div class="mb-4">
                                <div class="spinner-border text-primary" role="status" style="width: 4rem; height: 4rem;">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <h4 class="mb-3">Analyzing {{ task.platform }} profile "{{ task.profile_id }}"</h4>
                            <p class="mb-4">{{ task.message }}</p>
                            
                            <div class="progress mb-4" style="height: 25px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: {{ task.progress }}%;" 
                                     aria-valuenow="{{ task.progress }}" aria-valuemin="0" aria-valuemax="100">
                                    {{ task.progress }}%
                                </div>
                            </div>
                            
                            <p class="text-muted">This page will refresh automatically every 5 seconds.</p>
                        {% endif %}
                    </div>
                    <div class="card-footer">
                        <small class="text-muted">
                            Task ID: {{ task.task_id }}<br>
                            {% if task.start_time %}
                                Started: {{ task.start_time }}<br>
                            {% endif %}
                            {% if task.end_time %}
                                Completed: {{ task.end_time }}
                            {% endif %}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/main.js"></script>
    
    {% if task.status != "completed" and task.status != "failed" %}
    <script>
        // Automatic refresh handled by meta tag
        // Additional JS for animations or updates could go here
    </script>
    {% endif %}
</body>
</html>
    """,
    
    'result.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Results - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-lg-3 col-xl-2 d-none d-lg-block sidebar">
                <div class="card sticky-top">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Navigation</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        <a href="#summary" class="list-group-item list-group-item-action">Summary</a>
                        <a href="#timeline" class="list-group-item list-group-item-action">Timeline</a>
                        <a href="#personality" class="list-group-item list-group-item-action">Personality & Interests</a>
                        <a href="#writing" class="list-group-item list-group-item-action">Writing Style</a>
                        <a href="#authenticity" class="list-group-item list-group-item-action">Authenticity</a>
                        <a href="#predictions" class="list-group-item list-group-item-action">Predictions</a>
                    </div>
                    <div class="card-footer">
                        <div class="d-grid gap-2">
                            <a href="/api/tasks/{{ task.task_id }}/download" class="btn btn-sm btn-primary">
                                <i class="bi bi-download"></i> Download JSON
                            </a>
                            <a href="/" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-plus-circle"></i> New Analysis
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main content -->
            <div class="col-lg-9 col-xl-10">
                <!-- Summary Section -->
                <section id="summary" class="mb-5">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">Analysis Summary</h3>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h4>Profile Information</h4>
                                    <table class="table">
                                        <tr>
                                            <th>Platform:</th>
                                            <td>{{ result.metadata.platform|title }}</td>
                                        </tr>
                                        <tr>
                                            <th>Profile ID:</th>
                                            <td>{{ result.metadata.profile_id }}</td>
                                        </tr>
                                        <tr>
                                            <th>Analysis Date:</th>
                                            <td>{{ result.metadata.analysis_date }}</td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Key findings -->
                                    <h4 class="mt-4">Key Findings</h4>
                                    <ul class="list-group">
                                        {% if result.content_analysis.personality_traits %}
                                        <li class="list-group-item">
                                            <strong>Top traits:</strong> 
                                            {% for trait, value in result.content_analysis.personality_traits|dictsort(by='value', reverse=true)[:3] %}
                                                {{ trait|title }} ({{ (value * 100)|int }}%){% if not loop.last %}, {% endif %}
                                            {% endfor %}
                                        </li>
                                        {% endif %}
                                        
                                        {% if result.content_analysis.interests %}
                                        <li class="list-group-item">
                                            <strong>Top interests:</strong> 
                                            {% for interest, value in result.content_analysis.interests|dictsort(by='value', reverse=true)[:3] %}
                                                {{ interest|title }} ({{ (value * 100)|int }}%){% if not loop.last %}, {% endif %}
                                            {% endfor %}
                                        </li>
                                        {% endif %}
                                        
                                        {% if result.authenticity_analysis.overall_authenticity %}
                                        <li class="list-group-item">
                                            <strong>Authenticity score:</strong> 
                                            {{ (result.authenticity_analysis.overall_authenticity.score * 100)|int }}%
                                        </li>
                                        {% endif %}
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <!-- Personality radar chart placeholder -->
                                    <div class="chart-container">
                                        <canvas id="personalityChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                
                <!-- More sections would go here (Timeline, Personality & Interests, etc.) -->
                
                <!-- Predictions Section -->
                <section id="predictions" class="mb-5">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">Predictions & Forecasts</h3>
                        </div>
                        <div class="card-body">
                            {% if result.predictions.disclaimer %}
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle"></i> {{ result.predictions.disclaimer }}
                            </div>
                            {% endif %}
                            
                            <div class="row">
                                <!-- Future interests -->
                                {% if result.predictions.future_interests %}
                                <div class="col-md-6 mb-4">
                                    <h4>Predicted Future Interests</h4>
                                    <div class="list-group">
                                        {% for interest in result.predictions.future_interests %}
                                        <div class="list-group-item">
                                            <h5 class="mb-1">{{ interest.interest }}</h5>
                                            <div class="progress mb-2">
                                                <div class="progress-bar" role="progressbar" 
                                                     style="width: {{ (interest.confidence * 100)|int }}%;" 
                                                     aria-valuenow="{{ (interest.confidence * 100)|int }}" 
                                                     aria-valuemin="0" aria-valuemax="100">
                                                    {{ (interest.confidence * 100)|int }}%
                                                </div>
                                            </div>
                                            <p class="mb-1"><small>{{ interest.reasoning }}</small></p>
                                        </div>
                                        {% endfor %}
                                    </div>
                                </div>
                                {% endif %}
                                
                                <!-- Demographic predictions -->
                                {% if result.predictions.demographic_predictions %}
                                <div class="col-md-6 mb-4">
                                    <h4>Demographic Predictions</h4>
                                    <table class="table">
                                        <tbody>
                                            {% if result.predictions.demographic_predictions.age_range %}
                                            <tr>
                                                <th>Age Range:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.age_range.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.age_range.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.age_range.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                            
                                            {% if result.predictions.demographic_predictions.education_level %}
                                            <tr>
                                                <th>Education:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.education_level.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.education_level.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.education_level.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                            
                                            {% if result.predictions.demographic_predictions.occupation_category %}
                                            <tr>
                                                <th>Occupation:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.occupation_category.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.occupation_category.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.occupation_category.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                        </tbody>
                                    </table>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize charts
        document.addEventListener('DOMContentLoaded', function() {
            // Personality chart
            {% if result.content_analysis.personality_traits %}
            const personalityCtx = document.getElementById('personalityChart').getContext('# SocialInsight: Web API and Interface
# A web-based interface for the Social Media Profile Analyzer

from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import os
import json
import threading
import datetime
import time
import uuid
import logging
from typing import Dict, List, Any, Optional

# Import the analyzer core
from social_media_analyzer import SocialMediaAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='socialinsight_web.log'
)
logger = logging.getLogger('SocialInsightWeb')

# Initialize Flask app
app = Flask(__name__, 
          static_url_path='/static',
          template_folder='templates')

# Configure app
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize analyzer in global context
analyzer = SocialMediaAnalyzer()

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
            "message": self.message
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
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Mark as complete
        task.complete(result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        task.fail(str(e))


# API Routes
@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint to check service status"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint to start analysis"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if "platform" not in data or "profile_id" not in data:
            return jsonify({"error": "Missing required fields: platform, profile_id"}), 400
            
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
        thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
        thread.daemon = True
        thread.start()
        
        # Return task info
        return jsonify({
            "task_id": task_id,
            "status": "pending",
            "message": "Analysis task created"
        })
        
    except Exception as e:
        logger.error(f"Error creating analysis task: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error creating analysis task: {str(e)}"}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """API endpoint to check task status"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>/result', methods=['GET'])
def api_task_result(task_id):
    """API endpoint to get task result"""
    if task_id not in analysis_tasks:
        return jsonify(
            
# v3

// Personality chart
            {% if result.content_analysis.personality_traits %}
            const personalityCtx = document.getElementById('personalityChart').getContext('2d');
            const traits = {{ result.content_analysis.personality_traits|tojson }};
            const traitLabels = Object.keys(traits).map(t => t.charAt(0).toUpperCase() + t.slice(1));
            const traitValues = Object.values(traits);
            
            new Chart(personalityCtx, {
                type: 'radar',
                data: {
                    labels: traitLabels,
                    datasets: [{
                        label: 'Personality Traits',
                        data: traitValues,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                    }]
                },
                options: {
                    elements: {
                        line: {
                            tension: 0.1
                        }
                    },
                    scales: {
                        r: {
                            angleLines: {
                                display: true
                            },
                            suggestedMin: 0,
                            suggestedMax: 1
                        }
                    }
                }
            });
            {% endif %}
            
            // More charts would be initialized here
        });
    </script>
</body>
</html>
    """,
    
    'dashboard.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h3 class="card-title mb-0">Analysis Tasks</h3>
                        <a href="/" class="btn btn-light btn-sm">
                            <i class="bi bi-plus"></i> New Analysis
                        </a>
                    </div>
                    <div class="card-body">
                        {% if not tasks %}
                        <div class="alert alert-info">
                            No analysis tasks found. <a href="/">Start a new analysis</a>.
                        </div>
                        {% else %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Task ID</th>
                                        <th>Platform</th>
                                        <th>Profile</th>
                                        <th>Status</th>
                                        <th>Progress</th>
                                        <th>Start Time</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for task_id, task in tasks.items() %}
                                    <tr>
                                        <td><small class="text-muted">{{ task_id[:8] }}...</small></td>
                                        <td>{{ task.platform|title }}</td>
                                        <td>{{ task.profile_id }}</td>
                                        <td>
                                            {% if task.status == 'completed' %}
                                            <span class="badge bg-success">Completed</span>
                                            {% elif task.status == 'failed' %}
                                            <span class="badge bg-danger">Failed</span>
                                            {% elif task.status == 'running' %}
                                            <span class="badge bg-primary">Running</span>
                                            {% else %}
                                            <span class="badge bg-secondary">Pending</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <div class="progress" style="height: 10px;">
                                                <div class="progress-bar {% if task.status == 'failed' %}bg-danger{% endif %}" 
                                                     role="progressbar" style="width: {{ task.progress }}%;" 
                                                     aria-valuenow="{{ task.progress }}" aria-valuemin="0" aria-valuemax="100">
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {% if task.start_time %}
                                            <small>{{ task.start_time }}</small>
                                            {% else %}
                                            -
                                            {% endif %}
                                        </td>
                                        <td>
                                            {% if task.status == 'completed' %}
                                            <a href="/results/{{ task_id }}" class="btn btn-sm btn-primary me-1">
                                                <i class="bi bi-eye"></i>
                                            </a>
                                            <a href="/api/tasks/{{ task_id }}/download" class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-download"></i>
                                            </a>
                                            {% elif task.status == 'running' or task.status == 'pending' %}
                                            <a href="/tasks/{{ task_id }}" class="btn btn-sm btn-primary">
                                                <i class="bi bi-arrow-clockwise"></i> Monitor
                                            </a>
                                            {% else %}
                                            <a href="/" class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-arrow-repeat"></i> Retry
                                            </a>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """,
    
    'error.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow text-center">
                    <div class="card-header bg-danger text-white">
                        <h3 class="mb-0">Error</h3>
                    </div>
                    <div class="card-body p-5">
                        <div class="mb-4">
                            <i class="bi bi-exclamation-triangle-fill text-danger" style="font-size: 5rem;"></i>
                        </div>
                        <h4 class="mb-4">{{ error }}</h4>
                        <a href="/" class="btn btn-primary">Return to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
}


# CSS for the web interface (would be in static/css/style.css)
css_template = """
/* SocialInsight CSS Styles */
:root {
    --primary: #4a6fa5;
    --secondary: #6c757d;
    --success: #28a745;
    --danger: #dc3545;
    --warning: #ffc107;
    --info: #17a2b8;
    --light: #f8f9fa;
    --dark: #343a40;
}

body {
    background-color: #f5f5f5;
    color: #333;
}

.navbar-brand {
    font-weight: bold;
}

/* Sidebar styles */
.sidebar {
    margin-bottom: 20px;
}

.sidebar .card {
    border-radius: 10px;
    overflow: hidden;
}

.sidebar .card-header {
    font-weight: bold;
}

.sidebar .list-group-item {
    border-left: none;
    border-right: none;
    padding: 0.75rem 1.25rem;
}

.sidebar .list-group-item:first-child {
    border-top: none;
}

.sidebar .sticky-top {
    top: 20px;
}

/* Card styles */
.card {
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border: none;
}

.card-header {
    font-weight: bold;
    border-bottom: none;
}

.card-header.bg-primary {
    background-color: var(--primary) !important;
}

/* Chart containers */
.chart-container {
    position: relative;
    height: 300px;
    width: 100%;
}

/* Progress bars */
.progress {
    background-color: #e9ecef;
    border-radius: 10px;
    height: 10px;
    margin-bottom: 10px;
}

.progress-bar {
    background-color: var(--primary);
    border-radius: 10px;
}

/* Timeline styles */
.timeline-container {
    position: relative;
    padding-left: 50px;
}

.timeline-container::before {
    content: '';
    position: absolute;
    left: 20px;
    top: 0;
    bottom: 0;
    width: 2px;
    background-color: var(--primary);
}

.timeline-item {
    position: relative;
    margin-bottom: 30px;
}

.timeline-dot {
    position: absolute;
    left: -50px;
    top: 0;
    width: 20px;
    height: 20px;
    background-color: var(--primary);
    border-radius: 50%;
    border: 3px solid white;
}

.timeline-content {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Footer styles */
footer {
    background-color: #f8f9fa;
    color: var(--secondary);
    padding: 20px 0;
    margin-top: 50px;
}

/* Responsive adjustments */
@media (max-width: 992px) {
    .sidebar {
        margin-bottom: 30px;
    }
    
    .chart-container {
        height: 250px;
    }
}
"""


# JavaScript for the web interface (would be in static/js/main.js)
js_template = """
// SocialInsight main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add event listener for platform selection
    const platformSelect = document.getElementById('platform');
    if (platformSelect) {
        platformSelect.addEventListener('change', function() {
            const platform = this.value;
            const profileInput = document.getElementById('profile_id');
            
            if (platform === 'twitter') {
                profileInput.placeholder = 'Enter Twitter/X username (without @)';
            } else if (platform === 'facebook') {
                profileInput.placeholder = 'Enter Facebook profile ID or username';
            }
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Function to toggle sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const content = section.querySelector('.section-content');
    const icon = section.querySelector('.toggle-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    } else {
        content.style.display = 'none';
        icon.classList.remove('bi-chevron-up');
        icon.classList.add('bi-chevron-down');
    }
}

// AJAX function to refresh task status
function refreshTaskStatus(taskId) {
    fetch(`/api/tasks/${taskId}`)
        .then(response => response.json())
        .then(data => {
            // Update progress bar
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${data.progress}%`;
                progressBar.setAttribute('aria-valuenow', data.progress);
                progressBar.textContent = `${data.progress}%`;
            }
            
            // Update status message
            const statusMessage = document.getElementById('status-message');
            if (statusMessage) {
                statusMessage.textContent = data.message;
            }
            
            // If completed or failed, update the UI accordingly
            if (data.status === 'completed') {
                window.location.href = `/results/${taskId}`;
            } else if (data.status === 'failed') {
                document.getElementById('loading-spinner').style.display = 'none';
                document.getElementById('error-message').textContent = data.error;
                document.getElementById('error-container').style.display = 'block';
            } else {
                // Continue polling if still in progress
                setTimeout(() => refreshTaskStatus(taskId), 2000);
            }
        })
        .catch(error => {
            console.error('Error refreshing task status:', error);
        });
}
"""


# Add a helper to render templates from our template dictionary
def render_template_str(template_name, **context):
    """Render a template from our templates dictionary"""
    from jinja2 import Template
    template_str = html_templates.get(template_name)
    if not template_str:
        return f"Template {template_name} not found"
    
    template = Template(template_str)
    return template.render(**context)


# Override Flask's render_template
app.jinja_env.globals.update(tojson=json.dumps)

def render_template(template_name, **context):
    """Override Flask's render_template to use our dictionary-based templates"""
    return render_template_str(template_name, **context)


# Create static files
def create_static_files():
    """Create static files for the web interface"""
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    with open('static/css/style.css', 'w') as f:
        f.write(css_template)
    
    with open('static/js/main.js', 'w') as f:
        f.write(js_template)
    
    # A placeholder for the logo would be created here
    # In a real application, you would have an actual logo file


# Main entry point
if __name__ == "__main__":
    create_static_files()
    app.run(host='0.0.0.0', port=5000, debug=True)
{"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    
    if task.status != "completed":
        return jsonify({"error": "Task not completed", "status": task.status}), 400
    
    # Get result from memory or file
    if task.result:
        return jsonify(task.result)
    else:
        # Try to load from file
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Result not found"}), 404

@app.route('/api/tasks/<task_id>/download', methods=['GET'])
def api_task_download(task_id):
    """API endpoint to download result as file"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    
    if task.status != "completed":
        return jsonify({"error": "Task not completed", "status": task.status}), 400
    
    # Check if result file exists
    result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
    if not os.path.exists(result_path):
        return jsonify({"error": "Result file not found"}), 404
    
    return send_file(
        result_path,
        mimetype='application/json',
        as_attachment=True,
        download_name=f"analysis_{task.platform}_{task.profile_id}.json"
    )


# Web Interface Routes
@app.route('/')
def home():
    """Homepage with analysis form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def web_analyze():
    """Web form handler to start analysis"""
    platform = request.form.get('platform', '').lower()
    profile_id = request.form.get('profile_id', '')
    
    # Validate inputs
    if not platform or not profile_id:
        return render_template('index.html', error="Please provide both platform and profile ID")
    
    if platform not in ["twitter", "facebook"]:
        return render_template('index.html', error=f"Unsupported platform: {platform}")
    
    # Create analysis task (same as API)
    task_id = str(uuid.uuid4())
    task = AnalysisTask(task_id, platform, profile_id)
    analysis_tasks[task_id] = task
    
    # Start analysis in background
    thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
    thread.daemon = True
    thread.start()
    
    # Redirect to monitoring page
    return redirect(url_for('task_monitor', task_id=task_id))

@app.route('/tasks/<task_id>')
def task_monitor(task_id):
    """Page to monitor task progress"""
    if task_id not in analysis_tasks:
        return render_template('error.html', error="Task not found")
    
    task = analysis_tasks[task_id]
    return render_template('task.html', task=task)

@app.route('/results/<task_id>')
def view_result(task_id):
    """Page to view analysis results"""
    if task_id not in analysis_tasks:
        return render_template('error.html', error="Task not found")
    
    task = analysis_tasks[task_id]
    
    if task.status != "completed":
        return redirect(url_for('task_monitor', task_id=task_id))
    
    # Load result if not in memory
    if not task.result:
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                task.result = json.load(f)
        else:
            return render_template('error.html', error="Result not found")
    
    return render_template('result.html', task=task, result=task.result)

@app.route('/dashboard')
def dashboard():
    """Admin dashboard to see all tasks"""
    tasks = {tid: task.to_dict() for tid, task in analysis_tasks.items()}
    return render_template('dashboard.html', tasks=tasks)


# HTML Templates (would be in separate files in templates directory)
# For brevity, including them as string templates

html_templates = {
    'index.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialInsight - Social Media Profile Analyzer</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="card-title mb-0">Analyze Social Media Profile</h3>
                    </div>
                    <div class="card-body">
                        {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                        {% endif %}
                        
                        <form action="/analyze" method="post">
                            <div class="mb-3">
                                <label for="platform" class="form-label">Social Media Platform</label>
                                <select class="form-select" id="platform" name="platform" required>
                                    <option value="" selected disabled>Select a platform</option>
                                    <option value="twitter">Twitter / X</option>
                                    <option value="facebook">Facebook</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="profile_id" class="form-label">Profile ID / Username</label>
                                <input type="text" class="form-control" id="profile_id" name="profile_id" 
                                       placeholder="Enter profile username or ID" required>
                                <div class="form-text">Enter the username or profile ID you want to analyze.</div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Collection Method</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_api" value="api" checked>
                                    <label class="form-check-label" for="method_api">API Access (Recommended)</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_web" value="web">
                                    <label class="form-check-label" for="method_web">Web Scraping</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="method" id="method_manual" value="manual">
                                    <label class="form-check-label" for="method_manual">Manual Input</label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Analysis Options</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_sentiment" id="include_sentiment" value="true" checked>
                                    <label class="form-check-label" for="include_sentiment">Include sentiment analysis</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_authenticity" id="include_authenticity" value="true" checked>
                                    <label class="form-check-label" for="include_authenticity">Include authenticity analysis</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="include_predictions" id="include_predictions" value="true" checked>
                                    <label class="form-check-label" for="include_predictions">Include predictions</label>
                                </div>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary">Start Analysis</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h4 class="mb-0">About SocialInsight</h4>
                    </div>
                    <div class="card-body">
                        <p>SocialInsight is an open-source tool designed to analyze publicly available social media profiles
                        and generate insights about personality traits, interests, writing style, and more.</p>
                        
                        <p><strong>Key Features:</strong></p>
                        <ul>
                            <li>Collection of public profile data (posts, images, links)</li>
                            <li>Personality trait analysis based on content</li>
                            <li>Interest and preference identification</li>
                            <li>Timeline generation and visualization</li>
                            <li>Writing style analysis</li>
                            <li>Authenticity evaluation and fake profile detection</li>
                            <li>Predictive analysis based on patterns</li>
                        </ul>
                        
                        <div class="alert alert-info mt-3">
                            <strong>Privacy Notice:</strong> SocialInsight only analyzes publicly available information.
                            No private data is accessed or stored without explicit permission.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>
    """,
    
    'task.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis in Progress - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="card-title mb-0">Analysis in Progress</h3>
                    </div>
                    <div class="card-body text-center p-5">
                        {% if task.status == "completed" %}
                            <div class="mb-4">
                                <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="mb-3">Analysis Complete!</h4>
                            <p class="mb-4">The analysis of {{ task.platform }} profile "{{ task.profile_id }}" has been completed successfully.</p>
                            <a href="/results/{{ task.task_id }}" class="btn btn-primary btn-lg">View Results</a>
                            
                        {% elif task.status == "failed" %}
                            <div class="mb-4">
                                <i class="bi bi-x-circle-fill text-danger" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="mb-3">Analysis Failed</h4>
                            <p class="text-danger mb-4">{{ task.error }}</p>
                            <a href="/" class="btn btn-primary btn-lg">Try Again</a>
                            
                        {% else %}
                            <div class="mb-4">
                                <div class="spinner-border text-primary" role="status" style="width: 4rem; height: 4rem;">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <h4 class="mb-3">Analyzing {{ task.platform }} profile "{{ task.profile_id }}"</h4>
                            <p class="mb-4">{{ task.message }}</p>
                            
                            <div class="progress mb-4" style="height: 25px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: {{ task.progress }}%;" 
                                     aria-valuenow="{{ task.progress }}" aria-valuemin="0" aria-valuemax="100">
                                    {{ task.progress }}%
                                </div>
                            </div>
                            
                            <p class="text-muted">This page will refresh automatically every 5 seconds.</p>
                        {% endif %}
                    </div>
                    <div class="card-footer">
                        <small class="text-muted">
                            Task ID: {{ task.task_id }}<br>
                            {% if task.start_time %}
                                Started: {{ task.start_time }}<br>
                            {% endif %}
                            {% if task.end_time %}
                                Completed: {{ task.end_time }}
                            {% endif %}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/main.js"></script>
    
    {% if task.status != "completed" and task.status != "failed" %}
    <script>
        // Automatic refresh handled by meta tag
        // Additional JS for animations or updates could go here
    </script>
    {% endif %}
</body>
</html>
    """,
    
    'result.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Results - SocialInsight</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo.png" alt="SocialInsight Logo" height="30">
                SocialInsight
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/documentation">Documentation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-lg-3 col-xl-2 d-none d-lg-block sidebar">
                <div class="card sticky-top">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Navigation</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        <a href="#summary" class="list-group-item list-group-item-action">Summary</a>
                        <a href="#timeline" class="list-group-item list-group-item-action">Timeline</a>
                        <a href="#personality" class="list-group-item list-group-item-action">Personality & Interests</a>
                        <a href="#writing" class="list-group-item list-group-item-action">Writing Style</a>
                        <a href="#authenticity" class="list-group-item list-group-item-action">Authenticity</a>
                        <a href="#predictions" class="list-group-item list-group-item-action">Predictions</a>
                    </div>
                    <div class="card-footer">
                        <div class="d-grid gap-2">
                            <a href="/api/tasks/{{ task.task_id }}/download" class="btn btn-sm btn-primary">
                                <i class="bi bi-download"></i> Download JSON
                            </a>
                            <a href="/" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-plus-circle"></i> New Analysis
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main content -->
            <div class="col-lg-9 col-xl-10">
                <!-- Summary Section -->
                <section id="summary" class="mb-5">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">Analysis Summary</h3>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h4>Profile Information</h4>
                                    <table class="table">
                                        <tr>
                                            <th>Platform:</th>
                                            <td>{{ result.metadata.platform|title }}</td>
                                        </tr>
                                        <tr>
                                            <th>Profile ID:</th>
                                            <td>{{ result.metadata.profile_id }}</td>
                                        </tr>
                                        <tr>
                                            <th>Analysis Date:</th>
                                            <td>{{ result.metadata.analysis_date }}</td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Key findings -->
                                    <h4 class="mt-4">Key Findings</h4>
                                    <ul class="list-group">
                                        {% if result.content_analysis.personality_traits %}
                                        <li class="list-group-item">
                                            <strong>Top traits:</strong> 
                                            {% for trait, value in result.content_analysis.personality_traits|dictsort(by='value', reverse=true)[:3] %}
                                                {{ trait|title }} ({{ (value * 100)|int }}%){% if not loop.last %}, {% endif %}
                                            {% endfor %}
                                        </li>
                                        {% endif %}
                                        
                                        {% if result.content_analysis.interests %}
                                        <li class="list-group-item">
                                            <strong>Top interests:</strong> 
                                            {% for interest, value in result.content_analysis.interests|dictsort(by='value', reverse=true)[:3] %}
                                                {{ interest|title }} ({{ (value * 100)|int }}%){% if not loop.last %}, {% endif %}
                                            {% endfor %}
                                        </li>
                                        {% endif %}
                                        
                                        {% if result.authenticity_analysis.overall_authenticity %}
                                        <li class="list-group-item">
                                            <strong>Authenticity score:</strong> 
                                            {{ (result.authenticity_analysis.overall_authenticity.score * 100)|int }}%
                                        </li>
                                        {% endif %}
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <!-- Personality radar chart placeholder -->
                                    <div class="chart-container">
                                        <canvas id="personalityChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                
                <!-- More sections would go here (Timeline, Personality & Interests, etc.) -->
                
                <!-- Predictions Section -->
                <section id="predictions" class="mb-5">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">Predictions & Forecasts</h3>
                        </div>
                        <div class="card-body">
                            {% if result.predictions.disclaimer %}
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle"></i> {{ result.predictions.disclaimer }}
                            </div>
                            {% endif %}
                            
                            <div class="row">
                                <!-- Future interests -->
                                {% if result.predictions.future_interests %}
                                <div class="col-md-6 mb-4">
                                    <h4>Predicted Future Interests</h4>
                                    <div class="list-group">
                                        {% for interest in result.predictions.future_interests %}
                                        <div class="list-group-item">
                                            <h5 class="mb-1">{{ interest.interest }}</h5>
                                            <div class="progress mb-2">
                                                <div class="progress-bar" role="progressbar" 
                                                     style="width: {{ (interest.confidence * 100)|int }}%;" 
                                                     aria-valuenow="{{ (interest.confidence * 100)|int }}" 
                                                     aria-valuemin="0" aria-valuemax="100">
                                                    {{ (interest.confidence * 100)|int }}%
                                                </div>
                                            </div>
                                            <p class="mb-1"><small>{{ interest.reasoning }}</small></p>
                                        </div>
                                        {% endfor %}
                                    </div>
                                </div>
                                {% endif %}
                                
                                <!-- Demographic predictions -->
                                {% if result.predictions.demographic_predictions %}
                                <div class="col-md-6 mb-4">
                                    <h4>Demographic Predictions</h4>
                                    <table class="table">
                                        <tbody>
                                            {% if result.predictions.demographic_predictions.age_range %}
                                            <tr>
                                                <th>Age Range:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.age_range.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.age_range.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.age_range.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                            
                                            {% if result.predictions.demographic_predictions.education_level %}
                                            <tr>
                                                <th>Education:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.education_level.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.education_level.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.education_level.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                            
                                            {% if result.predictions.demographic_predictions.occupation_category %}
                                            <tr>
                                                <th>Occupation:</th>
                                                <td>
                                                    {{ result.predictions.demographic_predictions.occupation_category.prediction }}
                                                    <div class="progress mt-1" style="height: 5px;">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: {{ (result.predictions.demographic_predictions.occupation_category.confidence * 100)|int }}%">
                                                        </div>
                                                    </div>
                                                    <small class="text-muted">Confidence: {{ (result.predictions.demographic_predictions.occupation_category.confidence * 100)|int }}%</small>
                                                </td>
                                            </tr>
                                            {% endif %}
                                        </tbody>
                                    </table>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 SocialInsight. Open-source software.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms" class="text-decoration-none me-3">Terms of Use</a>
                    <a href="https://github.com/socialinsight" class="text-decoration-none">GitHub</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize charts
        document.addEventListener('DOMContentLoaded', function() {
            // Personality chart
            {% if result.content_analysis.personality_traits %}
            const personalityCtx = document.getElementById('personalityChart').getContext('# SocialInsight: Web API and Interface
# A web-based interface for the Social Media Profile Analyzer

from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import os
import json
import threading
import datetime
import time
import uuid
import logging
from typing import Dict, List, Any, Optional

# Import the analyzer core
from social_media_analyzer import SocialMediaAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='socialinsight_web.log'
)
logger = logging.getLogger('SocialInsightWeb')

# Initialize Flask app
app = Flask(__name__, 
          static_url_path='/static',
          template_folder='templates')

# Configure app
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize analyzer in global context
analyzer = SocialMediaAnalyzer()

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
            "message": self.message
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
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Mark as complete
        task.complete(result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        task.fail(str(e))


# API Routes
@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint to check service status"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint to start analysis"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if "platform" not in data or "profile_id" not in data:
            return jsonify({"error": "Missing required fields: platform, profile_id"}), 400
            
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
        thread = threading.Thread(target=run_analysis, args=(task_id, platform, profile_id))
        thread.daemon = True
        thread.start()
        
        # Return task info
        return jsonify({
            "task_id": task_id,
            "status": "pending",
            "message": "Analysis task created"
        })
        
    except Exception as e:
        logger.error(f"Error creating analysis task: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error creating analysis task: {str(e)}"}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """API endpoint to check task status"""
    if task_id not in analysis_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = analysis_tasks[task_id]
    return jsonify(task.to_dict())

@app.route('/api/tasks/<task_id>/result', methods=['GET'])
def api_task_result(task_id):
    """API endpoint to get task result"""
    if task_id not in analysis_tasks:
        return jsonify(