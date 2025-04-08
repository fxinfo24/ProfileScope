"""
ProfileScope Web Package
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
import os
from .models import db


def create_app(config=None):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///" + os.path.join(app.instance_path, "profilescope.db"),
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        RESULTS_FOLDER=os.path.join(app.instance_path, "results"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    )

    # Load additional configuration if provided
    if config:
        app.config.update(config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config["UPLOAD_FOLDER"])
        os.makedirs(app.config["RESULTS_FOLDER"])
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Import models
        from .models import Task

        # Create database tables
        db.create_all()

        # Register blueprints
        from .routes.views import views_bp
        from .routes.api import api_bp

        app.register_blueprint(views_bp)
        app.register_blueprint(api_bp)

        # Register template filters
        from .utils import filters

        app.jinja_env.filters["datetime"] = filters.format_datetime
        app.jinja_env.filters["duration"] = filters.format_duration
        app.jinja_env.filters["status_badge"] = filters.status_badge
        app.jinja_env.filters["number"] = filters.format_number
        app.jinja_env.filters["truncate"] = filters.truncate
        app.jinja_env.filters["percentage"] = filters.percentage
        app.jinja_env.filters["join_list"] = filters.join_list
        app.jinja_env.filters["format_json"] = filters.format_json

        # Register error handlers
        from .error_handlers import register_error_handlers

        register_error_handlers(app)

    return app
