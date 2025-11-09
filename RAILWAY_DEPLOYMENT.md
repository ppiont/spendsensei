# Railway Deployment Guide

This guide explains how to deploy both the frontend and backend of SpendSense to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed (optional, but recommended): `bun i -g @railway/cli`
3. Git repository pushed to GitHub/GitLab/Bitbucket

## Architecture

Railway will deploy two separate services:
- **Backend**: FastAPI Python application
- **Frontend**: SvelteKit Node.js application

## Deployment Steps

### Step 1: Create a New Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or your Git provider)
4. Select your `spendsensei` repository

### Step 2: Deploy the Backend

1. In your Railway project, click "New Service"
2. Select "GitHub Repo" and choose your repository
3. Railway will detect the `spendsense-backend` directory automatically
4. Configure the service:
   - **Root Directory**: `spendsense-backend`
   - **Builder**: Railpack (configured in `railway.json`)
   - Railway will auto-detect Python and use `uv` based on `pyproject.toml`
   - **Start Command**: `uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT` (configured in `railway.json`)

#### Backend Environment Variables

Set these in Railway's environment variables section:

- `PORT`: Automatically set by Railway (don't override)
- `DATABASE_URL`: Railway will provide a PostgreSQL database URL, but you can keep SQLite for now
- `CORS_ORIGINS_EXTRA`: Set this to your frontend's Railway URL (e.g., `https://your-frontend.railway.app`)
- `LOG_LEVEL`: `INFO` (default)

**Note**: Railway provides a `$PORT` environment variable that your app must use. The backend is configured to use this.

### Step 3: Deploy the Frontend

1. In the same Railway project, click "New Service" again
2. Select "GitHub Repo" and choose your repository
3. Configure the service:
   - **Root Directory**: `spendsense-frontend`
   - **Builder**: Railpack (configured in `railway.json`)
   - Railway will auto-detect Node.js and use `bun` based on `bun.lock`
   - **Start Command**: `node build/index.js` (configured in `railway.json`)

#### Frontend Environment Variables

Set these in Railway's environment variables section:

- `PORT`: Automatically set by Railway (don't override)
- `VITE_API_BASE_URL`: Set this to your backend's Railway URL (e.g., `https://your-backend.railway.app`)
- `NODE_ENV`: `production`

**Important**: Since Vite environment variables are embedded at build time, you'll need to rebuild the frontend whenever `VITE_API_BASE_URL` changes.

### Step 4: Configure Service URLs

After both services are deployed:

1. **Get Backend URL**: 
   - Go to your backend service in Railway
   - Click on the service
   - Copy the generated domain (e.g., `spendsense-backend-production.up.railway.app`)

2. **Get Frontend URL**:
   - Go to your frontend service in Railway
   - Copy the generated domain (e.g., `spendsense-frontend-production.up.railway.app`)

3. **Update Environment Variables**:
   - **Backend**: Set `CORS_ORIGINS_EXTRA` to your frontend URL (e.g., `https://spendsense-frontend-production.up.railway.app`)
   - **Frontend**: Set `VITE_API_BASE_URL` to your backend URL (e.g., `https://spendsense-backend-production.up.railway.app`)
   - **Rebuild** the frontend service after setting `VITE_API_BASE_URL`

### Step 5: Custom Domains (Optional)

Railway provides default `.railway.app` domains, but you can add custom domains:

1. Go to your service settings
2. Click "Settings" → "Networking"
3. Add your custom domain
4. Update DNS records as instructed
5. Update environment variables with the new domain

## Configuration Files

The following files have been created for Railway deployment:

### Backend
- `spendsense-backend/railway.json`: Railway configuration using Railpack builder
- Railpack will auto-detect Python and use `uv` based on `pyproject.toml`

### Frontend
- `spendsense-frontend/railway.json`: Railway configuration using Railpack builder
- `spendsense-frontend/svelte.config.js`: Updated to use `@sveltejs/adapter-node`
- Railpack will auto-detect Node.js and use `bun` based on `bun.lock`

## Database Considerations

Currently, the backend uses SQLite stored in the `data/` directory. For production:

1. **Option 1: Use Railway PostgreSQL** (Recommended)
   - Add a PostgreSQL service in Railway
   - Update `DATABASE_URL` to use the PostgreSQL connection string
   - Update the backend code to use PostgreSQL instead of SQLite

2. **Option 2: Use Railway Volume** (For SQLite)
   - Add a volume to your backend service
   - Mount it to `/data` or update `DATABASE_URL` to point to the volume path
   - Note: SQLite on volumes can have issues with concurrent writes

## Troubleshooting

### Backend Issues

- **Port binding**: Ensure your start command uses `$PORT` (Railway sets this automatically)
- **CORS errors**: Verify `CORS_ORIGINS_EXTRA` includes your frontend URL
- **Database errors**: Check that the database path is writable and accessible

### Frontend Issues

- **API connection errors**: Verify `VITE_API_BASE_URL` is set correctly and the frontend was rebuilt
- **Build failures**: Check that `@sveltejs/adapter-node` is installed
- **Runtime errors**: Check Railway logs for Node.js errors

### Viewing Logs

1. Go to your service in Railway
2. Click on "Deployments"
3. Click on a deployment to view logs
4. Or use Railway CLI: `railway logs`

## Continuous Deployment

Railway automatically deploys when you push to your connected branch. To configure:

1. Go to service settings
2. Click "Settings" → "Source"
3. Select the branch to deploy from (usually `main` or `master`)

## Monitoring

Railway provides:
- **Metrics**: CPU, memory, network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

Access these from your service dashboard in Railway.

## Cost Considerations

Railway offers:
- **Free tier**: $5 credit per month
- **Hobby plan**: $5/month for additional resources
- **Pro plan**: $20/month for production features

Check [railway.app/pricing](https://railway.app/pricing) for current pricing.

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [SvelteKit Adapters](https://kit.svelte.dev/docs/adapters)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

