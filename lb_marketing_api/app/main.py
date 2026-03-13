
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db, SessionLocal
from . import models
from .auth import get_current_user
from .routers import businesses, locations, social_profiles, campaigns, assets, posts, oauth, auth, pdfs, ai
from .routers.demo import engagements as demo_engagements
from .routers.demo import tasks as demo_tasks
from .routers.demo import audit as demo_audit
from .routers.demo import reviews as demo_reviews
from .routers.demo import month_end as demo_month_end

# Set up logging
logger = logging.getLogger(__name__)


def _seed_dev_test_user(db: Session) -> None:
    """Seed test user (email=test, password=test) with admin permissions. Development only."""
    existing = db.query(models.User).filter(models.User.email == "test").first()
    if existing:
        return
    test_user = models.User(email="test", full_name="Test Admin")
    test_user.set_password("test")
    db.add(test_user)
    db.commit()
    logger.info("Development: Seeded test user (email=test, password=test)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup code
    logger.info("=== Application startup event triggered ===")
    logger.info(f"APP_ENV: {settings.APP_ENV}")
    
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Development: Tables created via create_all()")
        # Seed test user (test/test) with admin permissions — development only
        try:
            db = SessionLocal()
            try:
                _seed_dev_test_user(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Development seed (test user) skipped: {e}")
    
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
    if not db.query(models.User).first():
        adminUser = models.User(email="admin@example.com",  full_name="Admin User")
        adminUser.set_password("password")
        db.add(adminUser)
        try:
            db.commit()
            db.refresh(adminUser)
        except Exception as e:
            db.rollback()
            error_msg = f"Could not create admin user: {str(e)}"
            raise HTTPException(
                detail=error_msg
            )
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
app.include_router(pdfs.router)
app.include_router(ai.router)
app.include_router(demo_engagements.router)
app.include_router(demo_tasks.router)
app.include_router(demo_audit.router)
app.include_router(demo_reviews.router)
app.include_router(demo_month_end.router)
