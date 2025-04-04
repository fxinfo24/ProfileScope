# app/web/app.py
from flask import Flask
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="socialinsight_web.log",
)
logger = logging.getLogger("SocialInsightWeb")

# Initialize Flask app
app = Flask(__name__, static_url_path="/static", template_folder="templates")

# Configure app
app.config["SECRET_KEY"] = "your_secret_key_here"  # Change in production
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["RESULTS_FOLDER"] = "results"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Create necessary directories
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)

# Import routes
from app.web.routes import api, views


# Create static files if they don't exist
def create_static_files():
    """Create static files for the web interface if they don't exist"""
    os.makedirs("app/web/static/css", exist_ok=True)
    os.makedirs("app/web/static/js", exist_ok=True)
    os.makedirs("app/web/static/img", exist_ok=True)

    # Check if style.css exists, create if not
    css_file = "app/web/static/css/style.css"
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write("/* SocialInsight CSS will go here */")

    # Check if main.js exists, create if not
    js_file = "app/web/static/js/main.js"
    if not os.path.exists(js_file):
        with open(js_file, "w") as f:
            f.write("// SocialInsight JavaScript will go here")


# Create static files when app is initialized
create_static_files()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
