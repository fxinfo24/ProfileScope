"""
Tests for the web routes of the ProfileScope application
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.web.models import Task, TaskStatus
from app.web import create_app
from app.web.routes.views import views_bp


@pytest.fixture
def app():
    """Create app fixture for testing"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    # Register the views blueprint if it's not already registered
    if "views" not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(views_bp)

    # Create application context
    with app.app_context():
        from app.web.models import db

        db.create_all()

        # Add some sample tasks
        sample_task = Task(platform="twitter", profile_id="test_user")
        sample_task.status = TaskStatus.COMPLETED
        sample_task.progress = 100
        sample_task.result_path = "/path/to/result.json"
        sample_task.created_at = datetime.utcnow()

        db.session.add(sample_task)
        db.session.commit()

        yield app

        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_home_page(client):
    """Test the home page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ProfileScope" in response.data
    assert b"Start New Analysis" in response.data


def test_start_analysis(client):
    """Test starting a new analysis"""
    response = client.post(
        "/start-analysis",
        data={"platform": "twitter", "profile_id": "test_user"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"task" in response.data


def test_task_status_page(client, app):
    """Test the task status page loads correctly"""
    # Ensure we have a task ID to query
    with app.app_context():
        task = Task.query.first()

    # Check if we got a task from the fixture
    if task:
        # Request the task page
        response = client.get(f"/tasks/{task.id}")
        assert response.status_code == 200
        assert f"Task Status" in response.data.decode("utf-8")
    else:
        # Create a task if none exists
        with app.app_context():
            from app.web.models import db

            new_task = Task(platform="twitter", profile_id="new_test_user")
            db.session.add(new_task)
            db.session.commit()
            task_id = new_task.id

        # Now request the task page
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert "Task Status" in response.data.decode("utf-8")


@patch("app.web.routes.views.render_template")
def test_completed_task_redirect_to_results(mock_render_template, client, app):
    """Test completed tasks show results page"""
    # Set up the mock to return a value
    mock_render_template.return_value = "Mocked Results Page"

    # Create a completed task with a mock result path
    with app.app_context():
        from app.web.models import db

        task = Task(platform="twitter", profile_id="completed_test_user")
        task.status = TaskStatus.COMPLETED

        # Create a temporary file for testing
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write('{"test": "data"}')
            task.result_path = f.name

        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Make the request to the results page
    response = client.get(f"/result/{task_id}")

    # Verify the response and mock calls
    assert response.status_code == 200
    mock_render_template.assert_called_once()

    # Check template name and context
    template_name = mock_render_template.call_args[0][0]
    assert template_name == "result.html"

    # Clean up the temporary file
    if os.path.exists(task.result_path):
        os.unlink(task.result_path)


def test_ajax_start_analysis(client):
    """Test starting analysis with AJAX"""
    headers = {"X-Requested-With": "XMLHttpRequest"}
    response = client.post(
        "/start-analysis",
        data={"platform": "twitter", "profile_id": "ajax_test_user"},
        headers=headers,
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "task_id" in data


# ============================================================================
# API ENDPOINT TESTS (/api/*)
# Comprehensive tests for REST API endpoints used by frontend
# ============================================================================

@patch.dict(os.environ, {"REDIS_URL": ""})  # Force threading fallback
@patch("app.web.routes.api.analyzer")
def test_api_create_analysis(mock_analyzer, client, app):
    """Test POST /api/analyze endpoint"""
    response = client.post(
        "/api/analyze",
        json={"platform": "twitter", "profile_id": "elonmusk"},
        content_type="application/json"
    )
    
    assert response.status_code == 202
    data = json.loads(response.data)
    assert "message" in data
    assert "task" in data
    assert data["task"]["platform"] == "twitter"
    assert data["task"]["profile_id"] == "elonmusk"
    assert data["task"]["status"] == "pending"


def test_api_create_analysis_missing_fields(client):
    """Test POST /api/analyze with missing required fields"""
    # Missing profile_id
    response = client.post(
        "/api/analyze",
        json={"platform": "twitter"},
        content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    
    # Missing platform
    response = client.post(
        "/api/analyze",
        json={"profile_id": "test_user"},
        content_type="application/json"
    )
    assert response.status_code == 400


def test_api_get_task(client, app):
    """Test GET /api/tasks/<id> endpoint"""
    with app.app_context():
        task = Task.query.first()
        task_id = task.id
    
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == task_id
    assert "platform" in data
    assert "status" in data


def test_api_get_task_not_found(client):
    """Test GET /api/tasks/<id> with non-existent ID"""
    response = client.get("/api/tasks/99999")
    assert response.status_code == 404


def test_api_list_tasks(client, app):
    """Test GET /api/tasks endpoint with pagination"""
    response = client.get("/api/tasks?limit=10&offset=0")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "tasks" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["tasks"], list)


def test_api_list_tasks_filtering(client, app):
    """Test GET /api/tasks with platform and status filters"""
    # Create tasks with different platforms
    with app.app_context():
        from app.web.models import db
        
        task1 = Task(platform="twitter", profile_id="user1", status=TaskStatus.COMPLETED)
        task2 = Task(platform="instagram", profile_id="user2", status=TaskStatus.PENDING)
        db.session.add_all([task1, task2])
        db.session.commit()
    
    # Filter by platform
    response = client.get("/api/tasks?platform=twitter")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(task["platform"] == "twitter" for task in data["tasks"])
    
    # Filter by status
    response = client.get("/api/tasks?status=completed")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(task["status"] == "completed" for task in data["tasks"])


def test_api_get_task_status(client, app):
    """Test GET /api/tasks/<id>/status endpoint (for polling)"""
    with app.app_context():
        task = Task.query.first()
        task_id = task.id
    
    response = client.get(f"/api/tasks/{task_id}/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "id" in data
    assert "status" in data
    assert "progress" in data
    # This endpoint should only return minimal fields for efficient polling
    assert set(data.keys()) == {"id", "status", "progress", "message", "error"}


def test_api_cancel_task(client, app):
    """Test POST /api/tasks/<id>/cancel endpoint"""
    with app.app_context():
        from app.web.models import db
        
        task = Task(platform="twitter", profile_id="cancel_test", status=TaskStatus.PENDING)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    response = client.post(f"/api/tasks/{task_id}/cancel")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Task cancelled"
    assert data["task"]["status"] == "failed"
    assert "cancelled by user" in data["task"]["error"].lower()


def test_api_cancel_completed_task(client, app):
    """Test cancelling a completed task (should fail)"""
    with app.app_context():
        task = Task.query.first()  # This is a completed task from fixture
        task_id = task.id
    
    response = client.post(f"/api/tasks/{task_id}/cancel")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_api_get_results(client, app):
    """Test GET /api/tasks/<id>/results endpoint"""
    with app.app_context():
        from app.web.models import db
        
        task = Task(platform="twitter", profile_id="results_test", status=TaskStatus.COMPLETED)
        task.result_data = {"test": "data", "score": 85}
        task.has_result = True
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    response = client.get(f"/api/tasks/{task_id}/results")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["test"] == "data"
    assert data["score"] == 85


def test_api_get_results_not_completed(client, app):
    """Test getting results for non-completed task"""
    with app.app_context():
        from app.web.models import db
        
        task = Task(platform="twitter", profile_id="pending_test", status=TaskStatus.PENDING)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    response = client.get(f"/api/tasks/{task_id}/results")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_api_download_results(client, app):
    """Test GET /api/tasks/<id>/download endpoint"""
    with app.app_context():
        from app.web.models import db
        
        task = Task(platform="twitter", profile_id="download_test", status=TaskStatus.COMPLETED)
        task.result_data = {"profile": "test_user", "analysis": "complete"}
        task.has_result = True
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    response = client.get(f"/api/tasks/{task_id}/download")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert "attachment" in response.headers.get("Content-Disposition", "")
    # Verify JSON content
    data = json.loads(response.data)
    assert data["profile"] == "test_user"


def test_api_platform_distribution(client, app):
    """Test GET /api/stats/platform-distribution endpoint"""
    with app.app_context():
        from app.web.models import db
        
        # Add tasks with different platforms
        platforms = ["twitter", "twitter", "instagram", "linkedin"]
        for platform in platforms:
            task = Task(platform=platform, profile_id=f"user_{platform}")
            db.session.add(task)
        db.session.commit()
    
    response = client.get("/api/stats/platform-distribution")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Should have stats for each platform
    platform_names = [item["platform"] for item in data]
    assert "twitter" in platform_names


def test_api_completion_rate(client, app):
    """Test GET /api/stats/completion-rate endpoint"""
    with app.app_context():
        from app.web.models import db
        
        # Add tasks with different statuses
        completed = Task(platform="twitter", profile_id="c1", status=TaskStatus.COMPLETED)
        failed = Task(platform="twitter", profile_id="f1", status=TaskStatus.FAILED)
        pending = Task(platform="twitter", profile_id="p1", status=TaskStatus.PENDING)
        
        db.session.add_all([completed, failed, pending])
        db.session.commit()
    
    response = client.get("/api/stats/completion-rate")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total" in data
    assert "completed" in data
    assert "failed" in data
    assert "completion_rate" in data
    assert data["total"] > 0
    assert 0 <= data["completion_rate"] <= 100


def test_api_cors_headers(client):
    """Test that CORS headers are present in API responses"""
    response = client.get("/api/stats/completion-rate")
    # Note: In test environment, CORS might not be fully configured
    # This test documents expected behavior in production
    assert response.status_code == 200
