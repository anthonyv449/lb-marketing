# Azure Functions Deployment Guide

This guide walks you through deploying the LB Marketing API to Azure Functions with Azure Database for PostgreSQL using the Azure Portal.

## Prerequisites

- Azure account with active subscription
- Python 3.12+ installed locally (for running migrations and local testing)
- Azure Functions Core Tools (optional, for local testing)

## Step 1: Create Azure Resources via Portal

### 1.1 Create Resource Group

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource** → **Resource group**
3. Configure:
   - **Name**: `lb-marketing-rg` (or your preferred name)
   - **Region**: Choose your preferred region (e.g., `East US`)
4. Click **Review + create** → **Create**

### 1.2 Create Azure Database for PostgreSQL

1. Go to **Create a resource** → **Azure Database for PostgreSQL**
2. Choose **Flexible Server** (recommended for production)
3. Configure the **Basics** tab:
   - **Subscription**: Your subscription
   - **Resource group**: Select the resource group created above
   - **Server name**: `lb-marketing-db` (must be globally unique)
   - **Region**: Same as resource group
   - **PostgreSQL version**: 16
   - **Workload type**: Development (or Production based on your needs)
4. Configure **Compute + storage**:
   - **Compute tier**: Burstable (B1ms) for dev, General Purpose for production
   - **Storage**: 32 GB minimum
5. Configure **Authentication**:
   - **Admin username**: `postgresadmin` (or your choice)
   - **Password**: Generate a strong password (save it securely!)
6. Configure **Networking**:
   - **Connectivity method**: Public access (or VNet for better security)
   - **Firewall rules**: 
     - Add your current IP address
     - Enable "Allow Azure services and resources to access this server"
7. Click **Review + create** → **Create**

### 1.3 Create Database

1. Once the server is created, go to the server resource
2. Click **Databases** → **Create**
3. **Database name**: `lbmarketing`
4. Click **Create**

### 1.4 Create Function App

1. Go to **Create a resource** → **Function App**
2. Configure the **Basics** tab:
   - **Subscription**: Your subscription
   - **Resource group**: Select the resource group created above
   - **Function App name**: `lb-marketing-api` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python
   - **Version**: 3.12
   - **Region**: Same as resource group
3. Configure **Hosting**:
   - **Operating System**: Linux
   - **Plan type**: Consumption (Serverless) for dev, Premium or Dedicated for production
4. Click **Review + create** → **Create**

## Step 2: Configure Function App Settings

### 2.1 Configure Application Settings

1. Go to your Function App in the Azure Portal
2. Navigate to **Configuration** → **Application settings**
3. Click **+ New application setting** and add the following:

| Setting Name | Value | Description |
|-------------|-------|-------------|
| `APP_NAME` | `LB Marketing API` | Application name |
| `APP_ENV` | `production` | Environment |
| `DATABASE_HOST` | `<your-db-server>.postgres.database.azure.com` | Database server FQDN (from Step 1.2) |
| `DATABASE_PORT` | `5432` | Database port |
| `DATABASE_USER` | `<your-db-admin-user>` | Database admin username |
| `DATABASE_PASSWORD` | `<your-db-password>` | Database password (saved from Step 1.2) |
| `DATABASE_NAME` | `lbmarketing` | Database name |
| `JWT_SECRET_KEY` | `<generate-random-secret>` | Strong random secret (use `openssl rand -hex 32`) |
| `CORS_ORIGINS` | `https://your-frontend.com` | Comma-separated frontend URLs (optional) |
| `TWITTER_CLIENT_ID` | `<your-twitter-client-id>` | Twitter OAuth client ID (if using) |
| `TWITTER_CLIENT_SECRET` | `<your-twitter-client-secret>` | Twitter OAuth secret (if using) |
| `TWITTER_REDIRECT_URI` | `https://<your-function-app>.azurewebsites.net/oauth/x/callback` | OAuth callback URL |
| `TWITTER_BEARER_TOKEN` | `<your-twitter-bearer-token>` | Twitter API bearer token (if using) |

4. Click **Save** to apply changes

**Important Security Notes:**
- Generate a strong `JWT_SECRET_KEY` using: `openssl rand -hex 32`
- Never commit secrets to version control
- Consider using Azure Key Vault for sensitive secrets in production

### 2.2 Configure Database Firewall

1. Go to your PostgreSQL server resource
2. Navigate to **Networking**
3. Ensure **Allow Azure services and resources to access this server** is enabled
4. Add your Function App's outbound IP addresses (found in Function App → **Properties** → **Outbound IP addresses**)

## Step 3: Deploy Your Application

### Option A: Deploy via Visual Studio Code

1. Install the [Azure Functions extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.azurefunctions) for VS Code
2. Open your project in VS Code
3. Sign in to Azure (click the Azure icon in the sidebar)
4. Right-click your Function App in Azure → **Deploy to Function App**
5. Select your Function App
6. Confirm deployment

### Option B: Deploy via Azure Portal (ZIP)

1. **Prepare deployment package:**
   ```bash
   cd lb_marketing_api
   # Create ZIP excluding unnecessary files
   zip -r deploy.zip . -x "*.git*" "*__pycache__*" "*.venv*" "*.env*" "*.vscode*"
   ```

2. **Deploy via Portal:**
   - Go to your Function App → **Deployment Center**
   - Choose **External Git** or **Local Git** (or use **ZIP Deploy**)
   - For ZIP Deploy:
     - Go to **Advanced Tools (Kudu)** → **Tools** → **Zip Push Deploy**
     - Upload your `deploy.zip` file

### Option C: Deploy via Azure Functions Core Tools

```bash
# Install Azure Functions Core Tools
# Windows: npm install -g azure-functions-core-tools@4
# Mac/Linux: See https://docs.microsoft.com/azure/azure-functions/functions-run-local

# Login to Azure
az login

# Deploy
cd lb_marketing_api
func azure functionapp publish <your-function-app-name>
```

### Option D: Deploy via GitHub Actions

1. Fork/clone this repository
2. Add the following secrets to your GitHub repository (Settings → Secrets):
   - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: Get from Function App → **Get publish profile**
   - `AZURE_FUNCTIONAPP_NAME`: Your Function App name
3. Update `azure-deploy.yml` with your Function App name
4. Push to main branch to trigger deployment

## Step 4: Run Database Migrations

### Option A: Run Migrations Locally (Before First Deployment)

1. **Set environment variables:**
   ```bash
   export DATABASE_HOST="<your-db-server>.postgres.database.azure.com"
   export DATABASE_PORT="5432"
   export DATABASE_USER="<your-db-admin-user>"
   export DATABASE_PASSWORD="<your-db-password>"
   export DATABASE_NAME="lbmarketing"
   ```

2. **Run migrations:**
   ```bash
   cd lb_marketing_api
   alembic upgrade head
   ```

### Option B: Migrations Run Automatically

The application runs migrations automatically on startup when `APP_ENV=production`. Check the Function App logs to verify migrations ran successfully.

### Option C: Run Migrations via Function App Console

1. Go to Function App → **Advanced Tools (Kudu)** → **Go**
2. Click **Debug console** → **CMD**
3. Navigate to your app directory
4. Set environment variables and run: `alembic upgrade head`

## Step 5: Verify Deployment

### 5.1 Check Function App Logs

1. Go to Function App → **Functions**
2. Click on your function → **Monitor** tab
3. Or go to **Log stream** to see real-time logs

### 5.2 Test Health Endpoint

```bash
curl https://<your-function-app>.azurewebsites.net/healthz
```

Expected response:
```json
{"status":"ok","env":"production"}
```

### 5.3 Check API Documentation

Visit: `https://<your-function-app>.azurewebsites.net/docs`

## Step 6: Configure Custom Domain (Optional)

1. Go to Function App → **Custom domains**
2. Click **Add custom domain**
3. Follow the instructions to verify domain ownership
4. Configure SSL certificate (Azure provides free SSL for Function Apps)

## Troubleshooting

### Function App Not Starting

1. **Check logs:**
   - Function App → **Log stream**
   - Or Function App → **Advanced Tools (Kudu)** → **Log files**

2. **Verify application settings:**
   - Function App → **Configuration** → **Application settings**
   - Ensure all required settings are present and correct

3. **Check Python version:**
   - Function App → **Configuration** → **General settings**
   - Ensure Python version is 3.12

### Database Connection Issues

1. **Check firewall rules:**
   - PostgreSQL server → **Networking**
   - Ensure Azure services are allowed
   - Add Function App outbound IPs if needed

2. **Verify connection string:**
   - Check `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` in application settings
   - Test connection using a database client

3. **Check SSL requirements:**
   - Azure PostgreSQL requires SSL by default
   - Ensure your connection string includes SSL parameters if needed

### Migration Issues

1. **Check Alembic configuration:**
   - Verify `alembic.ini` is in the root directory
   - Check that `alembic/env.py` correctly imports your models

2. **Run migrations manually:**
   - Use Function App console (Kudu) to run migrations
   - Or run locally with production database credentials

### CORS Issues

1. **Verify CORS_ORIGINS setting:**
   - Should be comma-separated URLs: `https://app1.com,https://app2.com`
   - Or leave empty for development (allows all origins)

## Production Best Practices

1. **Use Azure Key Vault** for storing secrets
2. **Enable Application Insights** for monitoring:
   - Function App → **Application Insights** → **Turn on Application Insights**
3. **Set up auto-scaling** (if using Consumption plan, this is automatic)
4. **Configure backup** for the database
5. **Enable HTTPS only** in Function App settings
6. **Set up monitoring alerts**
7. **Use staging slots** for zero-downtime deployments (Premium/Dedicated plans)
8. **Configure managed identity** for database access (instead of passwords)

## Cost Optimization

- Use **Consumption plan** for development/testing (pay per execution)
- Use **Premium plan** for production with predictable traffic
- Use **Burstable** tier for database in development
- Enable **auto-shutdown** for non-production environments (not applicable to Consumption plan)
- Use **Reserved Instances** for production database (1-3 year commitment)

## Local Development

### Running Locally

1. **Copy environment file:**
   ```bash
   cp local.settings.json.example local.settings.json
   # Edit local.settings.json with your local database settings
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run with Azure Functions Core Tools:**
   ```bash
   func start
   ```

4. **Or run with uvicorn (for FastAPI development):**
   ```bash
   uvicorn app.main:app --reload
   ```

## Next Steps

- Set up CI/CD pipeline
- Configure monitoring and alerts
- Set up staging environment
- Implement backup strategy
- Configure custom domain and SSL
- Set up Application Insights dashboards

## Support

For issues or questions:
- Azure Functions Documentation: https://docs.microsoft.com/azure/azure-functions/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Alembic Documentation: https://alembic.sqlalchemy.org/
