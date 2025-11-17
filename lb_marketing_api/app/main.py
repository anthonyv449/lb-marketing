
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from . import models
from .routers import businesses, locations, social_profiles, campaigns, assets, posts, oauth, auth

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
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
    # Run migrations in production (Azure Functions)
    elif settings.APP_ENV == "production":
        try:
            import alembic.config
            import os
            from pathlib import Path
            
            # Ensure we're using the correct path for alembic.ini
            alembic_ini_path = Path("alembic.ini")
            if not alembic_ini_path.exists():
                # Try alternative path (Azure Functions may have different working directory)
                alembic_ini_path = Path(__file__).parent.parent.parent / "alembic.ini"
            
            if alembic_ini_path.exists():
                alembic_cfg = alembic.config.Config(str(alembic_ini_path))
                from alembic import command
                command.upgrade(alembic_cfg, "head")
                print("✓ Database migrations completed successfully")
            else:
                print(f"⚠ Warning: alembic.ini not found at {alembic_ini_path}. Migrations skipped.")
        except Exception as e:
            import traceback
            error_msg = f"❌ ERROR: Could not run migrations: {e}\n{traceback.format_exc()}"
            print(error_msg)
            # In production, we want to know about migration failures
            # Consider logging to Application Insights or raising the error

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

# Routers
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(locations.router)
app.include_router(social_profiles.router)
app.include_router(campaigns.router)
app.include_router(assets.router)
app.include_router(posts.router)
app.include_router(oauth.router)
