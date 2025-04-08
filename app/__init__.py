"""
ProfileScope - Social Media Profile Analysis Tool
Core package initialization
"""

__version__ = "1.0.0"
__author__ = "ProfileScope Team"

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///profilescope.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
