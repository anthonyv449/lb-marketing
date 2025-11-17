"""
Azure Functions entry point for FastAPI application.
This file wraps the FastAPI app from app.main to work with Azure Functions.
"""

import azure.functions as func
from azure.functions import AsgiMiddleware
from app.main import app

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


