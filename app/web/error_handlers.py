"""
Error handlers for the web application
"""

from flask import render_template, Flask, jsonify


class HTTPError:
    def __init__(self, code: int, name: str, description: str):
        self.code = code
        self.name = name
        self.description = description


def register_handlers(app: Flask):
    """Register error handlers with Flask app"""

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return (
            render_template(
                "error.html",
                error={
                    "code": 404,
                    "name": "Page Not Found",
                    "description": "The requested page does not exist.",
                },
            ),
            404,
        )

    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 errors"""
        return (
            render_template(
                "error.html",
                error={
                    "code": 403,
                    "name": "Forbidden",
                    "description": "You do not have permission to access this resource.",
                },
            ),
            403,
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 errors"""
        return (
            render_template(
                "error.html",
                error={
                    "code": 500,
                    "name": "Internal Server Error",
                    "description": "An unexpected error occurred. Our team has been notified.",
                },
            ),
            500,
        )

    @app.errorhandler(400)
    def bad_request(e):
        """Handle 400 errors"""
        return (
            render_template(
                "error.html",
                error={
                    "code": 400,
                    "name": "Bad Request",
                    "description": "The request could not be understood by the server.",
                },
            ),
            400,
        )

    # Handle API errors with JSON responses
    @app.errorhandler(404)
    def api_not_found(e):
        """Handle 404 errors for API requests"""
        if request_wants_json():
            return jsonify({"error": "Not found", "code": 404}), 404
        return page_not_found(e)

    @app.errorhandler(500)
    def api_server_error(e):
        """Handle 500 errors for API requests"""
        if request_wants_json():
            return jsonify({"error": "Internal server error", "code": 500}), 500
        return internal_server_error(e)


def request_wants_json():
    """Check if the request is expecting JSON response"""
    from flask import request

    # Check if the request has Accept header with application/json
    # or if the request is an XHR request
    return (
        request.accept_mimetypes.best_match(["application/json", "text/html"])
        == "application/json"
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
