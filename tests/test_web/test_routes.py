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
