
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from . import models
from .auth import get_current_user
from .routers import businesses, locations, social_profiles, campaigns, assets, posts, oauth, auth

# Set up logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup code
    logger.info("=== Application startup event triggered ===")
    logger.info(f"APP_ENV: {settings.APP_ENV}")
    
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Development: Tables created via create_all()")
    
    yield  # Application runs here
    
    # Shutdown code (if needed)
    logger.info("Application shutting down")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*settings.CORS_ORIGINS] if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.APP_ENV}

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    # Simple seed example
    if not db.query(models.Business).first():
        acme = models.Business(name="ACME Coffee", email="hello@acme.test")
        db.add(acme)
        db.commit()
        db.refresh(acme)
        loc = models.Location(business_id=acme.id, name="Main St", city="LA", state="CA", timezone="America/Los_Angeles")
        db.add(loc)
        db.commit()
    return {"ok": True}

@app.post("/admin/migrate")
def run_migrations_manual(current_user: models.User = Depends(get_current_user)):
    """Manual migration endpoint - requires JWT token and user id must be 1"""
    # Check if user is authorized (must be user id 1)
    if current_user.id != 1:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: Only user with id 1 can run migrations"
        )
    
    try:
        import alembic.config
        from pathlib import Path
        from alembic import command
        
        logger.info("Manual migration endpoint called - running migrations from scratch")
        
        # Try multiple paths for alembic.ini
        possible_paths = [
            Path("alembic.ini"),
            Path(__file__).parent.parent.parent / "alembic.ini",
            Path("/home/site/wwwroot/alembic.ini"),  # Azure Functions Linux
            Path("D:/home/site/wwwroot/alembic.ini"),  # Azure Functions Windows
        ]
        
        alembic_ini_path = None
        checked_paths = []
        for path in possible_paths:
            exists = path.exists()
            checked_paths.append({"path": str(path), "exists": exists})
            if exists:
                alembic_ini_path = path
                break
        
        if not alembic_ini_path:
            return {
                "status": "error",
                "message": "alembic.ini not found",
                "current_directory": os.getcwd(),
                "checked_paths": checked_paths
            }
        
        logger.info(f"Found alembic.ini at: {alembic_ini_path}")
        alembic_cfg = alembic.config.Config(str(alembic_ini_path))
        original_cwd = os.getcwd()
        
        try:
            os.chdir(alembic_ini_path.parent)
            logger.info(f"Changed working directory to: {os.getcwd()}")
            
            # Run migrations from scratch: downgrade to base then upgrade to head
            logger.info("Downgrading to base (removing all migrations)...")
            command.downgrade(alembic_cfg, "base")
            
            logger.info("Upgrading to head (applying all migrations from scratch)...")
            command.upgrade(alembic_cfg, "head")
            
            logger.info("✓ Database migrations completed successfully from scratch")
            
            return {
                "status": "success",
                "message": "Migrations completed successfully from scratch",
                "alembic_ini_path": str(alembic_ini_path),
                "working_directory": os.getcwd(),
                "checked_paths": checked_paths
            }
        finally:
            os.chdir(original_cwd)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Migration error: {e}\n{error_traceback}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": error_traceback,
            "current_directory": os.getcwd()
        }

# Routers
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(locations.router)
app.include_router(social_profiles.router)
app.include_router(campaigns.router)
app.include_router(assets.router)
app.include_router(posts.router)
app.include_router(oauth.router)
