"""
Error handlers for the web application
"""

from flask import render_template


class HTTPError:
    def __init__(self, code: int, name: str, description: str):
        self.code = code
        self.name = name
        self.description = description


def register_error_handlers(app):
    """Register error handlers for the Flask application"""

    @app.errorhandler(400)
    def bad_request(e):
        error = HTTPError(
            400, "Bad Request", "The server could not understand your request."
        )
        return render_template("error.html", error=error), 400

    @app.errorhandler(401)
    def unauthorized(e):
        error = HTTPError(
            401, "Unauthorized", "Authentication is required to access this resource."
        )
        return render_template("error.html", error=error), 401

    @app.errorhandler(403)
    def forbidden(e):
        error = HTTPError(
            403, "Forbidden", "You don't have permission to access this resource."
        )
        return render_template("error.html", error=error), 403

    @app.errorhandler(404)
    def not_found(e):
        error = HTTPError(
            404,
            "Page Not Found",
            "The requested resource could not be found on this server.",
        )
        return render_template("error.html", error=error), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        error = HTTPError(
            405,
            "Method Not Allowed",
            "The method is not allowed for the requested URL.",
        )
        return render_template("error.html", error=error), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        error = HTTPError(
            429,
            "Too Many Requests",
            "You have sent too many requests in a given amount of time.",
        )
        return render_template("error.html", error=error), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        error = HTTPError(
            500, "Internal Server Error", "An unexpected error occurred on our servers."
        )
        return render_template("error.html", error=error), 500

    @app.errorhandler(503)
    def service_unavailable(e):
        error = HTTPError(
            503,
            "Service Unavailable",
            "The server is temporarily unable to handle your request.",
        )
        return render_template("error.html", error=error), 503
