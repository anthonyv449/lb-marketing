# Running Database Migrations on Azure

## Problem
Your database has no tables because migrations weren't run during deployment. The `alembic/versions/` directory is empty, so there are no migration files to run.

## Solution Options

### Option 1: Run Migrations via Azure Console (Recommended - No Re-deploy Needed)

This is the fastest way to fix your database without re-deploying.

#### Step 1: Create Migration File Locally

First, you need to create the initial migration file. Make sure you have your Python environment set up:

```bash
cd lb_marketing_api
pip install -r requirements.txt
python scripts/create_initial_migration.py
```

This will create a migration file in `alembic/versions/` directory.

#### Step 2: Upload Migration File to Azure

1. Go to your Azure Function App in the Azure Portal
2. Navigate to **Advanced Tools (Kudu)** → **Go**
3. Click **Debug console** → **CMD**
4. Navigate to your app directory: `cd site\wwwroot`
5. Navigate to the alembic versions directory: `cd alembic\versions`
6. Click the **+** button to create a new file
7. Copy the contents of your local migration file (from `alembic/versions/` directory)
8. Paste it into a new file with the same name (e.g., `xxxx_initial_migration.py`)

#### Step 3: Run Migration on Azure

1. In the Kudu console, navigate back to the root: `cd site\wwwroot`
2. Set environment variables (they should already be set, but verify):
   ```bash
   echo %DATABASE_HOST%
   echo %DATABASE_NAME%
   ```
3. Run the migration:
   ```bash
   python -m alembic upgrade head
   ```

**Note:** If `alembic` command is not available, you may need to install it first:
```bash
python -m pip install alembic
python -m alembic upgrade head
```

### Option 2: Create Migration Locally and Re-deploy

#### Step 1: Create Migration File

```bash
cd lb_marketing_api
pip install -r requirements.txt
python scripts/create_initial_migration.py
```

#### Step 2: Review Migration File

Check the generated file in `alembic/versions/` to ensure it looks correct.

#### Step 3: Re-deploy Your Application

Re-deploy your Function App using your preferred method (VS Code, GitHub Actions, ZIP deploy, etc.). The migration file will be included in the deployment.

#### Step 4: Run Migration

After deployment, migrations should run automatically on startup (if `APP_ENV=production`). Check the Function App logs to verify.

If automatic migration fails, use Option 1 (Azure Console) to run it manually.

### Option 3: Run Migration from Local Machine (If Database Allows External Connections)

If your Azure PostgreSQL database allows connections from your IP:

1. Create migration file locally:
   ```bash
   cd lb_marketing_api
   pip install -r requirements.txt
   python scripts/create_initial_migration.py
   ```

2. Set environment variables to point to your Azure database:
   ```powershell
   $env:DATABASE_HOST="<your-db-server>.postgres.database.azure.com"
   $env:DATABASE_PORT="5432"
   $env:DATABASE_USER="<your-db-user>"
   $env:DATABASE_PASSWORD="<your-db-password>"
   $env:DATABASE_NAME="<your-db-name>"
   ```

3. Run migration:
   ```bash
   alembic upgrade head
   ```

**Note:** Make sure your IP is added to the PostgreSQL firewall rules in Azure Portal.

## Verifying Migrations Ran Successfully

After running migrations, verify tables were created:

1. Go to Azure Portal → Your PostgreSQL Server → **Query editor**
2. Connect using your database credentials
3. Run:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

You should see tables like:
- `users`
- `businesses`
- `locations`
- `social_profiles`
- `campaigns`
- `media_assets`
- `scheduled_posts`
- `alembic_version` (tracks migration version)

## Troubleshooting

### Migration Fails with "No such revision" Error

This means the migration file wasn't found. Make sure:
- The migration file is in `alembic/versions/` directory
- The file name matches the pattern Alembic expects
- You're running the command from the correct directory

### Migration Fails with Database Connection Error

Check:
- Database firewall rules allow Azure services
- Function App outbound IPs are added to firewall
- Database credentials in Function App settings are correct
- Database server is running

### "alembic: command not found" in Azure Console

Install Alembic in the Azure console:
```bash
python -m pip install alembic
```

## Next Steps

After migrations are complete:
1. Verify all tables exist
2. Test your API endpoints
3. Consider setting up automatic migrations in your CI/CD pipeline (see `azure-deploy.yml`)

## Future Deployments

To prevent this issue in the future:
1. Always create migration files before deploying
2. Include migration files in your deployment
3. Consider adding a migration step to your CI/CD pipeline (already included in `azure-deploy.yml`)

