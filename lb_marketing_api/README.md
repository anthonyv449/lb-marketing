
# LB Marketing API (FastAPI + PostgreSQL)

A minimal, production-ready starter API for LB Marketing. Built with FastAPI and SQLAlchemy, backed by PostgreSQL.

## What's included
- FastAPI app with modular routers
- SQLAlchemy 2.0 ORM (sync) with session dependency
- Basic schema for: businesses, locations, social profiles, campaigns, media assets, scheduled posts
- CRUD endpoints for common operations
- Docker Compose for Postgres
- `.env` support

## Quick start (Dev)

1) Copy `.env.example` to `.env` and adjust as needed.
```bash
cp .env.example .env
```

2) Start Postgres with Docker:
```bash
docker compose up -d
```

3) Create a virtualenv and install deps:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4) Run the API:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive OpenAPI.

## Basic Entities

- **Business** → owns locations, social profiles, campaigns, assets, scheduled posts
- **Location** → address + timezone for a business
- **SocialProfile** → connection placeholder (Meta/IG/TikTok/X, etc.)
- **Campaign** → a grouping for scheduled posts
- **MediaAsset** → uploaded/hosted media reference (URL/Key + MIME type)
- **ScheduledPost** → content to publish at `scheduled_at` (status: scheduled/posted/failed/canceled)

> Note: For MVP we persist tokens/plain strings. Add KMS/KeyVault later for secrets.

## Database Migrations

This project uses Alembic for database migrations. In development, tables are created automatically on startup. In production, use migrations.

### Creating Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Initial Migration

To create the initial migration from your existing models:

```bash
python scripts/create_initial_migration.py
```

## Azure Deployment

This project is configured for deployment to Azure Functions with Azure Database for PostgreSQL.

### Quick Start

See [AZURE_QUICK_START.md](./AZURE_QUICK_START.md) for a 5-minute setup guide.

### Full Documentation

See [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md) for comprehensive deployment instructions.

### Key Files

- `function_app.py` - Azure Functions entry point
- `host.json` - Azure Functions configuration
- `local.settings.json.example` - Local development settings template
- `alembic/` - Database migration files
- `azure-deploy.yml` - GitHub Actions workflow for CI/CD

## Test Data
Use the `/seed` endpoint to insert a sample business and location.

## License
MIT (yours to change).
