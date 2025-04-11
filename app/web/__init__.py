"""
Web application package initialization
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy outside of create_app for importing in models
db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure the Flask app"""
    app = Flask(__name__, instance_relative_config=True)

    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///profilescope.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER="uploads",
        RESULTS_FOLDER="results",
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    )

    # Load instance config if it exists
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(
            os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"]), exist_ok=True
        )
        os.makedirs(
            os.path.join(app.instance_path, app.config["RESULTS_FOLDER"]), exist_ok=True
        )
    except OSError:
        pass

    # Initialize the database
    db.init_app(app)

    # Import and register blueprints
    from .routes.views import views_bp
    from .routes.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register error handlers
    from . import error_handlers

    error_handlers.register_handlers(app)

    # Register filters
    from . import filters  # Import from current package, not from utils

    filters.register_filters(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
