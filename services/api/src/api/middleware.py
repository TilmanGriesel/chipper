import os
from functools import wraps

from api.config import API_KEY, app, logger
from flask import abort, request


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_api_key = os.getenv("REQUIRE_API_KEY", "true")
        require_api_key = require_api_key.lower() == "true"

        if not require_api_key:
            return f(*args, **kwargs)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            abort(401, description="Invalid or missing API key")

        return f(*args, **kwargs)

    return decorated_function


def setup_security_middleware(app):
    @app.before_request
    def before_request():
        logger.info(
            f"Request {request.method} {request.path} from {request.remote_addr}"
        )
        if (
            os.getenv("REQUIRE_SECURE", "False").lower() == "true"
            and not request.is_secure
        ):
            logger.warning(f"Insecure request attempt from {request.remote_addr}")
            abort(403, description="HTTPS required")

    @app.after_request
    def after_request(response):
        response.headers.update(
            {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
        )

        if os.getenv("ENABLE_CORS", "False").lower() == "true":
            allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
            response.headers["Access-Control-Allow-Origin"] = allowed_origins
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"

        return response

    @app.errorhandler(401)
    def unauthorized_error(error):
        return {"error": "Unauthorized", "message": str(error.description)}, 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return {"error": "Forbidden", "message": str(error.description)}, 403

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }, 500


def setup_request_logging_middleware(app):
    @app.before_request
    def log_request_info():
        if request.path == "/" or request.path == "/health":
            return

        log_data = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "request_id": request.headers.get("X-Request-ID"),
        }

        logger.debug("Incoming request", extra=log_data)


def init_middleware(app):
    setup_security_middleware(app)
    setup_request_logging_middleware(app)
    logger.info("Middleware initialized successfully")


init_middleware(app)
