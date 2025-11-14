
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
            alembic_cfg = alembic.config.Config("alembic.ini")
            from alembic import command
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            print(f"Warning: Could not run migrations: {e}")

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
