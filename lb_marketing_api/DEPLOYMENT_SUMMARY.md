# Azure Functions Deployment Setup - Summary

This document summarizes all the Azure Functions deployment configuration that has been set up for the LB Marketing API.

## What Has Been Configured

### 1. Database Migrations (Alembic)
- ✅ Alembic added to `requirements.txt`
- ✅ Alembic configuration files created:
  - `alembic.ini` - Main Alembic configuration
  - `alembic/env.py` - Migration environment with database connection
  - `alembic/script.py.mako` - Migration template
  - `alembic/versions/` - Directory for migration files
- ✅ `app/main.py` updated to run migrations automatically in production
- ✅ Helper script: `scripts/create_initial_migration.py`

### 2. Azure Functions Configuration
- ✅ `function_app.py` - Azure Functions entry point using AsgiFunctionApp
- ✅ `host.json` - Azure Functions host configuration
- ✅ `local.settings.json.example` - Local development settings template
- ✅ `azure-deploy.yml` - GitHub Actions workflow for CI/CD

### 3. Configuration Updates
- ✅ `app/config.py` updated with:
  - Better comments for Azure-specific settings
  - CORS_ORIGINS validator to handle comma-separated strings from Azure App Settings
  - Support for Azure environment variable naming conventions

### 4. Documentation
- ✅ `AZURE_DEPLOYMENT.md` - Comprehensive deployment guide (Portal-based)
- ✅ `AZURE_QUICK_START.md` - Quick reference guide
- ✅ `README.md` - Updated with Azure Functions deployment section
- ✅ `.env.example` - Environment variable template (for local uvicorn)

### 5. Project Files
- ✅ `.gitignore` - Updated to exclude deployment artifacts

## Next Steps for Deployment

### 1. Create Initial Migration
```bash
cd lb_marketing_api
python scripts/create_initial_migration.py
# Review the generated migration file
alembic upgrade head  # Apply it locally first
```

### 2. Set Up Azure Resources via Portal

Follow the step-by-step instructions in `AZURE_DEPLOYMENT.md`:

1. Create Resource Group
2. Create Azure Database for PostgreSQL Flexible Server
3. Create Database
4. Create Function App

### 3. Configure Function App Settings

In Azure Portal → Function App → **Configuration** → **Application settings**, add:

- `APP_NAME` - Application name
- `APP_ENV` - Set to `production`
- `DATABASE_HOST` - Your PostgreSQL server FQDN
- `DATABASE_PORT` - `5432`
- `DATABASE_USER` - Database admin user
- `DATABASE_PASSWORD` - Database password
- `DATABASE_NAME` - Database name
- `JWT_SECRET_KEY` - Strong random secret (use `openssl rand -hex 32`)
- `CORS_ORIGINS` - Comma-separated frontend URLs (optional)
- Twitter OAuth credentials (if using)

### 4. Deploy Application

**Option A: Visual Studio Code (Recommended)**
- Install Azure Functions extension
- Right-click Function App → Deploy to Function App

**Option B: ZIP Deploy**
- Create ZIP file excluding unnecessary files
- Upload via Portal: Function App → Advanced Tools (Kudu) → Zip Push Deploy

**Option C: Azure Functions Core Tools**
```bash
func azure functionapp publish <your-function-app-name>
```

**Option D: GitHub Actions**
- Add secrets to your GitHub repository
- Update `azure-deploy.yml` with your Function App name
- Push to main branch

### 5. Run Migrations

Migrations will run automatically on startup via `app/main.py`, or run manually:
```bash
# Set environment variables
export DATABASE_HOST="<your-db-host>"
export DATABASE_USER="<your-db-user>"
export DATABASE_PASSWORD="<your-db-password>"
export DATABASE_NAME="<your-db-name>"

# Run migrations
alembic upgrade head
```

## File Structure

```
lb_marketing_api/
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
├── alembic.ini                  # Alembic configuration
├── app/
│   ├── config.py               # Updated for Azure
│   ├── main.py                 # FastAPI app (updated for production)
│   └── ...
├── function_app.py             # Azure Functions entry point
├── host.json                    # Azure Functions configuration
├── local.settings.json.example  # Local development settings
├── azure-deploy.yml            # GitHub Actions workflow
├── AZURE_DEPLOYMENT.md         # Full deployment guide (Portal)
├── AZURE_QUICK_START.md        # Quick reference
└── requirements.txt             # Updated with Azure Functions packages
```

## Key Features

1. **Production-Ready Migrations**: Uses Alembic instead of `create_all()`
2. **Automatic Migrations**: Runs on app startup in Azure Functions
3. **Azure Functions Integration**: Uses AsgiFunctionApp for seamless FastAPI support
4. **Portal-Based Setup**: All instructions use Azure Portal (no CLI required)
5. **Comprehensive Documentation**: Multiple guides for different skill levels
6. **CI/CD Ready**: GitHub Actions workflow included

## Security Notes

- ⚠️ Never commit `.env` files or secrets
- ⚠️ Use Azure Key Vault for production secrets (recommended)
- ⚠️ Generate strong `JWT_SECRET_KEY` (use `openssl rand -hex 32`)
- ⚠️ Configure database firewall rules properly
- ⚠️ Use HTTPS only in production
- ⚠️ Set appropriate CORS origins (not `*` in production)

## Local Development

### Using Azure Functions Core Tools
```bash
# Copy settings
cp local.settings.json.example local.settings.json
# Edit local.settings.json with your settings

# Run locally
func start
```

### Using uvicorn (FastAPI development)
```bash
# Copy .env.example to .env and edit
cp .env.example .env

# Run
uvicorn app.main:app --reload
```

## Support

For detailed instructions, see:
- `AZURE_QUICK_START.md` - Quick setup guide
- `AZURE_DEPLOYMENT.md` - Comprehensive guide
- `README.md` - General project documentation

## Troubleshooting

Common issues and solutions are documented in `AZURE_DEPLOYMENT.md` under the "Troubleshooting" section.
