# Azure Functions Quick Start Guide

This is a condensed guide for quickly deploying to Azure Functions. For detailed instructions, see [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md).

## Prerequisites

- Azure account
- Python 3.12+ installed locally

## Quick Setup (5 Minutes)

### 1. Create Resources via Portal

1. **Resource Group**: Create `lb-marketing-rg` in your preferred region
2. **PostgreSQL Flexible Server**:
   - Name: `lb-marketing-db` (must be unique)
   - Version: 16
   - Compute: Burstable B1ms (dev) or General Purpose (prod)
   - Admin: Set username and password (save password!)
   - Networking: Allow Azure services + your IP
3. **Database**: Create `lbmarketing` database
4. **Function App**:
   - Name: `lb-marketing-api` (must be unique)
   - Runtime: Python 3.12
   - Plan: Consumption (serverless)

### 2. Configure Function App Settings

Go to Function App → **Configuration** → **Application settings** and add:

```
APP_NAME=LB Marketing API
APP_ENV=production
DATABASE_HOST=<your-db-server>.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_USER=<your-db-admin-user>
DATABASE_PASSWORD=<your-db-password>
DATABASE_NAME=lbmarketing
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

**Generate JWT Secret:**
```bash
openssl rand -hex 32
```

### 3. Configure Database Firewall

1. PostgreSQL server → **Networking**
2. Enable "Allow Azure services and resources to access this server"
3. Get Function App outbound IPs: Function App → **Properties** → **Outbound IP addresses**
4. Add those IPs to firewall rules if needed

### 4. Deploy Application

**Option A: VS Code (Easiest)**
1. Install Azure Functions extension
2. Right-click Function App → **Deploy to Function App**

**Option B: ZIP Deploy**
```bash
cd lb_marketing_api
zip -r deploy.zip . -x "*.git*" "*__pycache__*" "*.venv*" "*.env*"
# Upload via Portal: Function App → Advanced Tools (Kudu) → Zip Push Deploy
```

**Option C: Azure Functions Core Tools**
```bash
func azure functionapp publish <your-function-app-name>
```

### 5. Run Migrations

Migrations run automatically on startup, or run manually:

```bash
# Set environment variables
export DATABASE_HOST="<your-db-host>"
export DATABASE_USER="<your-db-user>"
export DATABASE_PASSWORD="<your-db-password>"
export DATABASE_NAME="lbmarketing"

# Run migrations
cd lb_marketing_api
alembic upgrade head
```

### 6. Verify

```bash
# Test health endpoint
curl https://<your-function-app>.azurewebsites.net/healthz

# View API docs
open https://<your-function-app>.azurewebsites.net/docs
```

## Environment Variables Checklist

Required in Function App → **Configuration** → **Application settings**:

- ✅ `APP_NAME` - Application name
- ✅ `APP_ENV` - Set to `production`
- ✅ `DATABASE_HOST` - PostgreSQL server FQDN
- ✅ `DATABASE_PORT` - `5432`
- ✅ `DATABASE_USER` - Database admin user
- ✅ `DATABASE_PASSWORD` - Database password
- ✅ `DATABASE_NAME` - Database name
- ✅ `JWT_SECRET_KEY` - Strong random secret
- ⚠️ `CORS_ORIGINS` - Frontend URLs (comma-separated, optional)
- ⚠️ Twitter OAuth credentials (if using)

## Common Commands

```bash
# View logs
# Portal: Function App → Log stream

# Restart function app
# Portal: Function App → Overview → Restart

# Test locally
func start
# Or
uvicorn app.main:app --reload
```

## Troubleshooting

**Function won't start:**
- Check logs: Function App → **Log stream**
- Verify all application settings are set
- Check Python version is 3.12

**Database connection errors:**
- Verify firewall allows Azure services
- Check database credentials in app settings
- Test connection locally

**Migration errors:**
- Run migrations manually via Function App console (Kudu)
- Or run locally with production database credentials

## Next Steps

1. Set up custom domain
2. Configure SSL certificate
3. Enable Application Insights
4. Set up CI/CD pipeline
5. Configure monitoring alerts

For detailed information, see [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md).
