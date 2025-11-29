"""
ProfileScope Web Application
Flask web interface for the ProfileScope analyzer
"""

import os
import logging
from flask import Flask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/profilescope_web.log",
)
logger = logging.getLogger("ProfileScope.Web")

# Import db from models
from app.web.models import db


def create_app(test_config=None):
    """Create and configure the Flask application"""
    # Create Flask app instance
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="static",
        template_folder="templates",
    )

    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "profilescope.db")
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-key-for-development-only"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URI", f"sqlite:///{db_path}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        RESULTS_FOLDER=os.path.join(os.getcwd(), "data", "results"),
    )

    # Override default configuration
    if test_config:
        app.config.update(test_config)

    # Ensure instance folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)

    with app.app_context():
        # Import and register blueprints
        from .routes.api import api_bp
        from .routes.views import views_bp

        app.register_blueprint(api_bp, url_prefix="/api")
        app.register_blueprint(views_bp)

        # Import and register error handlers
        from .error_handlers import register_handlers

        register_handlers(app)

        # Import and register filters
        from .filters import register_filters

        register_filters(app)

        # Create database tables
        db.create_all()

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
