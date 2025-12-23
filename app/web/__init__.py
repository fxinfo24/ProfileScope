"""Web application package initialization.

Important:
- The canonical Flask app factory for this repository is `app/web/app.py:create_app`.
- This module re-exports that factory so imports like `from app.web import create_app`
  continue to work (tests rely on this).

We intentionally do NOT create a second `SQLAlchemy()` instance here, because the
application uses `app.web.models.db`.
"""

from .app import create_app  # re-export
from .models import db  # re-export shared SQLAlchemy instance
