"""
Azure Functions entry point for FastAPI application.
This file wraps the FastAPI app from app.main to work with Azure Functions.
"""

import logging
import azure.functions as func
from azure.functions import AsgiMiddleware
from app.main import app
from app.db import SessionLocal
from app.routers.posts import process_due_posts

# Set up logging
logger = logging.getLogger(__name__)

# Create ASGI middleware wrapper
asgi_handler = AsgiMiddleware(app)

# Create function app with manual HTTP trigger to control route pattern
function_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

class HttpRequestWrapper:
    """Wrapper for HttpRequest that strips /api prefix from the URL path."""
    def __init__(self, original_request: func.HttpRequest):
        self._original = original_request
        # Store original URL and create modified version
        from urllib.parse import urlparse, urlunparse
        original_url = original_request.url
        parsed = urlparse(original_url)
        
        # Strip /api from the path if it exists
        path = parsed.path
        if path.startswith('/api'):
            path = path[4:]  # Remove '/api'
            if not path:  # If path becomes empty, set to '/'
                path = '/'
        
        # Reconstruct URL with modified path
        self._modified_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
    
    def __getattr__(self, name):
        # Intercept URL access to return modified URL
        if name == 'url':
            return self._modified_url
        # Delegate all other attributes to the original request
        return getattr(self._original, name)

@function_app.route(route="{*path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def http_app_func(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function that handles all routes for FastAPI app."""
    # Wrap the request to strip /api prefix from URL before passing to FastAPI
    modified_req = HttpRequestWrapper(req)
    return await asgi_handler.handle_async(modified_req)

@function_app.timer_trigger(schedule="0 * * * * *", arg_name="timer", run_on_startup=False, use_monitor=False)
def publish_scheduled_posts_timer(timer: func.TimerRequest) -> None:
    """
    Timer-triggered function that runs every minute to publish scheduled posts.
    Schedule: "0 * * * * *" means run at the start of every minute (second 0 of every minute).
    """
    logger.info("Timer trigger fired: Starting scheduled posts publish process")
    
    db = SessionLocal()
    try:
        published_posts = process_due_posts(db)
        if published_posts:
            logger.info(f"Successfully published {len(published_posts)} scheduled post(s)")
        else:
            logger.info("No scheduled posts were due for publishing")
    except Exception as e:
        logger.error(f"Error in publish_scheduled_posts_timer: {str(e)}", exc_info=True)
    finally:
        db.close()


