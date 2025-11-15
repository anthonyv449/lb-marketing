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

@function_app.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def http_app_func(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function that handles all routes for FastAPI app."""
    return asgi_handler.handle(req)

