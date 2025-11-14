# Deployment Guide

This guide will help you deploy the LB Marketing UI to production.

## Prerequisites

- Node.js 18+ installed
- Backend API deployed and accessible
- Domain configured (optional, but recommended)

## Environment Variables

Create a `.env` file in the `lb-marketing-ui` directory (or set environment variables in your hosting platform):

```env
# API Configuration
# Set this to your backend API URL (e.g., https://api.yourdomain.com)
# Leave empty in development to use Vite proxy
VITE_API_URL=https://api.yourdomain.com
```

**Important**: 
- In development, leave `VITE_API_URL` empty to use the Vite proxy
- In production, set `VITE_API_URL` to your backend API URL
- All Vite environment variables must be prefixed with `VITE_`

## Building for Production

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set environment variables** (if not using .env file):
   ```bash
   # Windows PowerShell
   $env:VITE_API_URL="https://api.yourdomain.com"
   
   # Linux/Mac
   export VITE_API_URL="https://api.yourdomain.com"
   ```

3. **Build the application**:
   ```bash
   npm run build
   ```

4. **Preview the build locally** (optional):
   ```bash
   npm run preview
   ```

The build output will be in the `dist/` directory.

## Deployment Options

### Option 1: Vercel (Recommended - Easiest)

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Vite
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
     - **Install Command**: `npm install`
   - Add environment variable:
     - `VITE_API_URL` = `https://api.yourdomain.com`
   - Click Deploy

3. **Custom Domain** (optional):
   - Go to Project Settings → Domains
   - Add your domain (e.g., `app.yourdomain.com`)
   - Follow DNS configuration instructions

### Option 2: Netlify

1. **Install Netlify CLI** (optional):
   ```bash
   npm i -g netlify-cli
   ```

2. **Deploy**:
   - Go to [netlify.com](https://netlify.com)
   - Import your repository
   - Configure:
     - **Build command**: `npm run build`
     - **Publish directory**: `dist`
   - Add environment variable:
     - `VITE_API_URL` = `https://api.yourdomain.com`
   - Click Deploy

3. **Custom Domain**:
   - Go to Site Settings → Domain Management
   - Add custom domain

### Option 3: Azure Static Web Apps

1. **Create Static Web App in Azure Portal**:
   - Go to Azure Portal → Create Resource → Static Web App
   - Configure:
     - **Build Presets**: Custom
     - **App location**: `/`
     - **Api location**: (leave empty)
     - **Output location**: `dist`

2. **Configure Build**:
   - In Azure Portal → Your Static Web App → Build
   - Set build configuration:
     ```yaml
     app_location: "/"
     api_location: ""
     output_location: "dist"
     app_build_command: "npm run build"
     api_build_command: ""
     ```

3. **Add Environment Variables**:
   - Go to Configuration → Application Settings
   - Add: `VITE_API_URL` = `https://api.yourdomain.com`

4. **Custom Domain**:
   - Go to Custom Domains
   - Add your domain

### Option 4: Manual Deployment (Any Static Host)

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Upload the `dist/` folder** to your hosting provider:
   - FTP/SFTP to your server
   - Upload to web root directory
   - Ensure your server is configured to serve `index.html` for all routes (SPA routing)

3. **Configure your web server** (if using Nginx):
   ```nginx
   server {
       listen 80;
       server_name app.yourdomain.com;
       root /path/to/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

## Post-Deployment Checklist

- [ ] Verify the site loads correctly
- [ ] Check browser console for errors
- [ ] Test API connectivity (check Network tab)
- [ ] Verify environment variables are set correctly
- [ ] Test OAuth flow (if backend is deployed)
- [ ] Check mobile responsiveness
- [ ] Verify HTTPS is enabled

## Troubleshooting

### API calls failing
- Check that `VITE_API_URL` is set correctly
- Verify CORS is configured on your backend
- Check browser console for specific error messages

### OAuth not working
- Ensure backend is deployed and accessible
- Verify `VITE_API_URL` points to your backend
- Check that OAuth endpoints are configured correctly

### 404 errors on page refresh
- Ensure your hosting provider is configured for SPA routing
- For Nginx, add the `try_files` directive (see above)
- For Apache, create `.htaccess` with rewrite rules

### Build errors
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Clear build cache: `rm -rf dist .vite`

## Development vs Production

### Development
- Uses Vite dev server with proxy
- Hot module replacement (HMR)
- Source maps enabled
- No environment variable needed (uses proxy)

### Production
- Static files served from `dist/`
- Minified and optimized
- Requires `VITE_API_URL` environment variable
- No proxy - direct API calls

## Continuous Deployment

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Support

For issues or questions, check:
- Vite documentation: https://vitejs.dev
- Your hosting provider's documentation
- Backend API documentation

