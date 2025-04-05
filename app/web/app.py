"""
ProfileScope Web Application
Flask-based web interface for social media profile analysis
"""

import os
from pathlib import Path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from ..core.analyzer import SocialMediaAnalyzer
from .models import db
from .routes import register_blueprints


def create_app(config_path=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load default configuration
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-key-change-in-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///"
            + str(Path(__file__).parent.parent.parent / "data" / "profilescope.db"),
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(Path(__file__).parent.parent.parent / "data" / "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        ALLOWED_EXTENSIONS={"json"},
    )

    # Override with custom config if provided
    if config_path:
        app.config.from_json(config_path)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize database
    db.init_app(app)
    Migrate(app, db)

    # Register blueprints
    register_blueprints(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("error.html", error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("error.html", error=error), 500

    return app


def main():
    """Run the application"""
    app = create_app()

    # Get configuration from environment or use defaults
    host = os.environ.get("FLASK_HOST", "localhost")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
