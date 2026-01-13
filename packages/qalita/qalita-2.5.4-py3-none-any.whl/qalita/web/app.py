"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
from flask import Flask, request
from flask_socketio import SocketIO
from waitress import serve

# Global SocketIO instance
socketio = None

def create_app(config_obj) -> Flask:
    """Application factory for the QALITA CLI UI - API only."""
    global socketio

    app = Flask(__name__)
    app.config["QALITA_CONFIG_OBJ"] = config_obj
    app.config["SECRET_KEY"] = os.urandom(24)

    # Initialize SocketIO with CORS enabled
    # Try gevent first, fall back to threading if gevent causes issues (e.g., Python 3.13 compatibility)
    async_mode = "threading"  # Default to threading for better compatibility
    try:
        # Try to use gevent if available and working
        import sys
        if sys.version_info < (3, 13):
            # Only try gevent on Python < 3.13 due to zope.interface compatibility issues
            async_mode = "gevent"
    except Exception:
        pass

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode=async_mode,
        logger=False,
        engineio_logger=False,
    )

    # Register blueprints (API only, no templates)
    from qalita.web.blueprints.dashboard import bp as dashboard_bp
    from qalita.web.blueprints.context import bp as context_bp
    from qalita.web.blueprints.sources import bp as sources_bp
    from qalita.web.blueprints.workers import bp as workers_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(context_bp)
    app.register_blueprint(sources_bp, url_prefix="/sources")
    app.register_blueprint(workers_bp)  # No prefix - routes already include /worker/ and /agent/

    # Try to import qalita-studio if installed (optional dependency)
    try:
        from qalita_studio.api.blueprints.studio import bp as studio_bp
        from qalita_studio.api.blueprints.studio import register_studio_socketio_handlers
        app.register_blueprint(studio_bp, url_prefix="/studio")
        register_studio_socketio_handlers()
    except ImportError:
        pass  # qalita-studio not installed

    # CORS headers for Next.js frontend
    # IMPORTANT: Socket.IO requests must be completely bypassed from Flask middleware
    # as they don't follow standard WSGI flow and can cause "write() before start_response" errors
    @app.after_request
    def after_request(response):
        # Skip Socket.IO requests - they are handled by Socket.IO middleware and don't follow standard WSGI flow
        # We need to detect Socket.IO requests very early and return immediately to avoid WSGI protocol violations
        try:
            # Check WSGI environment PATH_INFO directly - this is the most reliable method
            # and works even if Flask's request context is in an invalid state
            environ = None
            if hasattr(request, 'environ'):
                environ = request.environ
            elif hasattr(request, '_get_current_object'):
                # Try to get the underlying request object
                try:
                    req_obj = request._get_current_object()
                    if hasattr(req_obj, 'environ'):
                        environ = req_obj.environ
                except (AttributeError, RuntimeError):
                    pass

            if environ:
                path_info = environ.get('PATH_INFO', '')
                # If this is a Socket.IO request, return immediately without any processing
                if path_info and path_info.startswith('/socket.io/'):
                    return response
        except (AttributeError, RuntimeError, KeyError, TypeError):
            # If we can't safely check, return response as-is to prevent WSGI violations
            return response

        # Only add CORS headers for non-Socket.IO requests
        # Also check that response object is valid before modifying
        try:
            if response and hasattr(response, 'headers'):
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        except (AttributeError, RuntimeError):
            # If response object is invalid, just return it as-is
            pass

        return response

    return app


def get_socketio():
    """Get the global SocketIO instance."""
    return socketio


def run_dashboard_ui(config_obj, host: str = "localhost", port: int = 7070):
    app = create_app(config_obj)
    socketio = get_socketio()
    url = f"http://{host}:{port}"
    print(f"QALITA CLI UI is running. Open {url}")
    # Use SocketIO's built-in server for WebSocket support
    if socketio:
        socketio.run(app, host=host, port=port, use_reloader=False, log_output=False, allow_unsafe_werkzeug=True)
    else:
        from waitress import serve
        serve(app, host=host, port=port)
