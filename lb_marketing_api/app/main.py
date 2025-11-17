
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from . import models
from .routers import businesses, locations, social_profiles, campaigns, assets, posts, oauth, auth

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*settings.CORS_ORIGINS] if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (development only)
# In production, use Alembic migrations instead
@app.on_event("startup")
async def on_startup():
    logger.info("=== Application startup event triggered ===")
    logger.info(f"APP_ENV: {settings.APP_ENV}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Development: Tables created via create_all()")
    # Run migrations in production (Azure Functions)
    elif settings.APP_ENV == "production":
        try:
            import alembic.config
            from pathlib import Path
            
            # Try multiple paths for alembic.ini (Azure Functions may have different working directory)
            possible_paths = [
                Path("alembic.ini"),
                Path(__file__).parent.parent.parent / "alembic.ini",
                Path("/home/site/wwwroot/alembic.ini"),  # Azure Functions Linux
                Path("D:/home/site/wwwroot/alembic.ini"),  # Azure Functions Windows
            ]
            
            alembic_ini_path = None
            for path in possible_paths:
                logger.info(f"Checking path: {path} (exists: {path.exists()})")
                if path.exists():
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
                    
                    from alembic import command
                    command.upgrade(alembic_cfg, "head")
                    logger.info("✓ Database migrations completed successfully")
                finally:
                    os.chdir(original_cwd)
            else:
                logger.warning(f"⚠ alembic.ini not found. Tried paths: {[str(p) for p in possible_paths]}")
        except Exception as e:
            import traceback
            logger.error(f"❌ ERROR: Could not run migrations: {e}")
            logger.error(traceback.format_exc())

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
def run_migrations_manual():
    """Manual migration endpoint - use for troubleshooting when automatic migrations fail"""
    try:
        import alembic.config
        from pathlib import Path
        
        logger.info("Manual migration endpoint called")
        
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
        
        if alembic_ini_path:
            logger.info(f"Found alembic.ini at: {alembic_ini_path}")
            alembic_cfg = alembic.config.Config(str(alembic_ini_path))
            original_cwd = os.getcwd()
            try:
                os.chdir(alembic_ini_path.parent)
                from alembic import command
                command.upgrade(alembic_cfg, "head")
                return {
                    "status": "success",
                    "message": "Migrations completed successfully",
                    "alembic_ini_path": str(alembic_ini_path),
                    "working_directory": os.getcwd(),
                    "checked_paths": checked_paths
                }
            finally:
                os.chdir(original_cwd)
        else:
            return {
                "status": "error",
                "message": "alembic.ini not found",
                "current_directory": os.getcwd(),
                "checked_paths": checked_paths
            }
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
