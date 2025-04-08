"""
Tests for the web routes
"""

import pytest
import os
import json
from datetime import datetime
import tempfile
import shutil

# Import from app package
from app.web.app import create_app
from app.web.models import db
from app.web.models.task import Task, TaskStatus


@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    # Create temporary directory for test results
    test_results_dir = tempfile.mkdtemp(prefix="profilescope_test_")

    # Create a test configuration
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "RESULTS_FOLDER": test_results_dir,
    }

    # Create the app with test config
    flask_app = create_app(test_config)

    # Create the test results directory
    os.makedirs(test_results_dir, exist_ok=True)

    # Create an application context
    with flask_app.app_context():
        # Create database tables
        db.create_all()
        yield flask_app
        # Clean up
        db.drop_all()

    # Remove temporary directory when done
    shutil.rmtree(test_results_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def sample_task(app):
    """Create a sample task for testing"""
    with app.app_context():
        task = Task(platform="twitter", profile_id="test_user")
        db.session.add(task)
        db.session.commit()

        # Get a fresh instance from the database
        task_id = task.id
        task = db.session.get(Task, task_id)

        yield task

        # Clean up
        db.session.delete(task)
        db.session.commit()


def test_home_page(client):
    """Test that the home page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ProfileScope" in response.data
    assert b"Start New Analysis" in response.data


def test_start_analysis(client):
    """Test starting a new analysis"""
    data = {
        "platform": "twitter",
        "profile_id": "test_user",
    }
    response = client.post("/start-analysis", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Task Status" in response.data


def test_task_status_page(client, sample_task):
    """Test viewing task status page"""
    # Make sure to use the app context to keep the session alive
    with client.application.app_context():
        response = client.get(f"/tasks/{sample_task.id}")
        assert response.status_code == 200
        assert bytes(sample_task.profile_id, "utf-8") in response.data


def test_completed_task_redirect_to_results(client, app):
    """Test that completed tasks redirect to results"""
    with app.app_context():
        # Create a completed task
        task = Task(platform="twitter", profile_id="test_user")
        task.status = TaskStatus.COMPLETED
        task.result_path = os.path.join(app.config["RESULTS_FOLDER"], f"{task.id}.json")
        db.session.add(task)
        db.session.commit()

        # Create mock result file
        os.makedirs(os.path.dirname(task.result_path), exist_ok=True)
        with open(task.result_path, "w") as f:
            json.dump({"metadata": {"profile_id": "test_user"}}, f)

    # Test redirect
    response = client.get(f"/results/{task.id}", follow_redirects=True)
    assert response.status_code == 200


def test_ajax_start_analysis(client):
    """Test starting analysis via AJAX"""
    data = {
        "platform": "twitter",
        "profile_id": "test_user",
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = client.post("/start-analysis", data=data, headers=headers)
    assert response.status_code == 200

    response_data = json.loads(response.data)
    assert "task_id" in response_data
