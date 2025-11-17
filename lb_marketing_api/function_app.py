"""
Azure Functions entry point for FastAPI application.
This file wraps the FastAPI app from app.main to work with Azure Functions.
"""

import logging
import os
from pathlib import Path

import azure.functions as func
from azure.functions import AsgiMiddleware

# Set up logging
logger = logging.getLogger(__name__)

# Run migrations at module import time (more reliable than lifespan events in Azure Functions)
def run_migrations_on_import():
    """Run migrations when module is imported - more reliable in Azure Functions."""
    try:
        from app.config import settings
        
        if settings.APP_ENV == "production":
            logger.info("=== Running migrations on module import (Azure Functions) ===")
            logger.info(f"APP_ENV: {settings.APP_ENV}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            import alembic.config
            from alembic import command
            
            # Try multiple paths for alembic.ini
            possible_paths = [
                Path("alembic.ini"),
                Path(__file__).parent / "alembic.ini",
                Path("/home/site/wwwroot/alembic.ini"),  # Azure Functions Linux
                Path("D:/home/site/wwwroot/alembic.ini"),  # Azure Functions Windows
            ]
            
            alembic_ini_path = None
            for path in possible_paths:
                exists = path.exists()
                logger.info(f"Checking path: {path} (exists: {exists})")
                if exists:
                    alembic_ini_path = path
                    break
            
            if alembic_ini_path:
                logger.info(f"Found alembic.ini at: {alembic_ini_path}")
                alembic_cfg = alembic.config.Config(str(alembic_ini_path))
                
                # Change to alembic.ini directory for proper path resolution
                original_cwd = os.getcwd()
                try:
                    os.chdir(alembic_ini_path.parent)
                    logger.info(f"Changed working directory to: {os.getcwd()}")
                    
                    command.upgrade(alembic_cfg, "head")
                    logger.info("✓ Database migrations completed successfully on module import")
                finally:
                    os.chdir(original_cwd)
            else:
                logger.warning(f"⚠ alembic.ini not found. Tried paths: {[str(p) for p in possible_paths]}")
                logger.warning(f"Current directory: {os.getcwd()}, __file__: {__file__}")
        else:
            logger.info(f"Skipping migrations (APP_ENV={settings.APP_ENV}, not production)")
    except Exception as e:
        import traceback
        logger.error(f"❌ ERROR: Could not run migrations on import: {e}")
        logger.error(traceback.format_exc())
        # Don't raise - allow app to start even if migrations fail

# Run migrations when this module is imported
run_migrations_on_import()

# Import app after migrations (app import may trigger lifespan, but we want migrations first)
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


