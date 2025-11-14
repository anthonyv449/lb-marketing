"""
Azure Functions entry point for FastAPI application.
This file wraps the FastAPI app from app.main to work with Azure Functions.
"""

import azure.functions as func
from app.main import app

# Wrap FastAPI app with Azure Functions ASGI handler
# This allows FastAPI to run on Azure Functions
function_app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)

