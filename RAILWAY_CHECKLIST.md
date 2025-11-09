# Railway Deployment Checklist & Validation

**Last Updated:** 2025-11-09
**Status:** ✅ Ready for Deployment

This document provides a step-by-step checklist for deploying SpendSense to Railway and validates all critical configuration.

## Pre-Deployment Checklist

### ✅ Critical Fixes Applied

- [x] **database.py uses config.py** - DATABASE_URL now reads from environment variable
- [x] **Railway.json configured** - Both frontend and backend have proper Railway configuration
- [x] **CORS configured** - Backend supports `CORS_ORIGINS_EXTRA` environment variable
- [x] **Frontend build works** - `bun run build` creates production-ready build/
- [x] **adapter-node installed** - Frontend uses @sveltejs/adapter-node for Railway
- [x] **Health check endpoints** - `/health` and `/` endpoints for monitoring
- [x] **Content catalogs tracked** - content_catalog.yaml and partner_offers_catalog.yaml in git

### ⚠️  Important Warnings

1. **Database Persistence**: Railway filesystem is ephemeral. SQLite data will be lost on container restart.
   - **Option A**: Use Railway Volume (mount to `/app/data`)
   - **Option B**: Use Railway PostgreSQL (recommended for production)
   - **Option C**: Accept data loss (OK for demo deployments)

2. **Database Initialization**: Database files (*.db) are gitignored and won't exist on first deployment
   - Run initialization script: `uv run python scripts/init_db_railway.py`
   - Or run full data generator: `uv run python scripts/init_and_load_data.py`

3. **Environment Variables**: Must be set BEFORE building frontend (Vite embeds at build time)

## Railway Deployment Steps

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `spendsensei` repository
4. Railway creates an empty project

### Step 2: Deploy Backend Service

1. In your Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → Choose your repository
3. Railway will use Railpack and auto-detect the configuration:
   - **Builder**: Railpack (from railway.json)
   - **Root Directory**: `spendsense-backend` (auto-detected)
   - **Runtime**: Python 3.13 (from pyproject.toml)
   - **Package Manager**: uv (auto-detected)
   - **Start Command**: `uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (in Railway UI):
   ```
   # Optional: override database URL (default: sqlite:///data/spendsense.db)
   DATABASE_URL=sqlite+aiosqlite:///data/spendsense.db

   # CORS: Set to frontend URL after frontend is deployed
   CORS_ORIGINS_EXTRA=https://your-frontend.railway.app

   # Logging
   LOG_LEVEL=INFO
   ```

5. **Deploy**: Railway automatically deploys
6. **Copy Backend URL**: e.g., `https://spendsense-backend-production.up.railway.app`

### Step 3: Deploy Frontend Service

1. In the same Railway project, click **"New Service"** again
2. Select **"GitHub Repo"** → Choose your repository
3. Railway will use Railpack and auto-detect the configuration:
   - **Builder**: Railpack (from railway.json)
   - **Root Directory**: `spendsense-frontend` (auto-detected)
   - **Runtime**: Node.js (from package.json)
   - **Package Manager**: bun (from bun.lock)
   - **Build Command**: `bun run build` (auto-detected)
   - **Start Command**: `node build/index.js`

4. **Set Environment Variables** (in Railway UI):
   ```
   # Required: Backend API URL from Step 2
   VITE_API_BASE_URL=https://your-backend.railway.app

   # Node environment
   NODE_ENV=production

   # Port (automatically set by Railway)
   PORT=$PORT
   ```

5. **Deploy**: Railway automatically builds and deploys
6. **Copy Frontend URL**: e.g., `https://spendsense-frontend-production.up.railway.app`

### Step 4: Update Cross-Origin Configuration

After both services are deployed:

1. **Update Backend CORS**:
   - Go to backend service → Variables
   - Set `CORS_ORIGINS_EXTRA=https://your-frontend.railway.app`
   - Backend will auto-redeploy

2. **Update Frontend API URL** (if needed):
   - Go to frontend service → Variables
   - Verify `VITE_API_BASE_URL=https://your-backend.railway.app`
   - **Important**: Click "Redeploy" to rebuild with new env var

### Step 5: Initialize Database

**Option A: Use Railway CLI** (Recommended)
```bash
# Install Railway CLI
bun i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Select backend service and run init script
railway run --service spendsense-backend uv run python scripts/init_and_load_data.py
```

**Option B: Use Railway Volume** (For persistence)
1. Go to backend service → Settings → Volumes
2. Add new volume: `/app/data`
3. Deploy with volume mounted
4. Run initialization script (data persists across deployments)

**Option C: Use PostgreSQL** (Production recommended)
1. Add PostgreSQL service to Railway project
2. Copy PostgreSQL connection string
3. Set `DATABASE_URL` in backend environment variables
4. Update SQLAlchemy models if needed for PostgreSQL compatibility

### Step 6: Verify Deployment

Test the following endpoints:

**Backend Health:**
```bash
curl https://your-backend.railway.app/health
# Expected: {"status":"healthy","service":"spendsense-api"}
```

**Backend API Docs:**
```
https://your-backend.railway.app/docs
```

**Frontend:**
```
https://your-frontend.railway.app
```

**Test Full Flow:**
1. Open frontend URL
2. Check that API calls work (Dashboard loads)
3. Try switching users in dropdown
4. Verify Insights page shows recommendations

## Configuration Files Reference

### Backend: `spendsense-backend/railway.json`
```json
{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "RAILPACK"
    },
    "deploy": {
        "startCommand": "uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 10
    }
}
```

### Frontend: `spendsense-frontend/railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "node build/index.js",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto-set | - | Railway sets automatically |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///data/spendsense.db` | Database connection string |
| `CORS_ORIGINS_EXTRA` | Yes | - | Frontend URL (comma-separated if multiple) |
| `LOG_LEVEL` | No | `INFO` | Python logging level |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto-set | - | Railway sets automatically |
| `VITE_API_BASE_URL` | Yes | - | Backend API URL |
| `NODE_ENV` | No | `production` | Node environment |

**Important**: `VITE_API_BASE_URL` is embedded at build time. Must redeploy frontend if changed.

## Troubleshooting

### Backend Issues

**Problem**: `500 Internal Server Error` or CORS errors
**Solution**:
- Check `CORS_ORIGINS_EXTRA` includes frontend URL
- Verify backend logs: Railway → Service → Deployments → View Logs

**Problem**: Database errors on startup
**Solution**:
- Run initialization script: `railway run uv run python scripts/init_db_railway.py`
- Check data directory is writable
- Consider using Railway volume for persistence

**Problem**: Module import errors after reorganization
**Solution**:
- Verify all imports use new module structure (ingest/, features/, personas/, etc.)
- Check database.py imports settings from config.py

### Frontend Issues

**Problem**: API calls fail with CORS or network errors
**Solution**:
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend CORS includes frontend URL
- Rebuild frontend: Railway → Service → Deployments → Redeploy

**Problem**: Build fails with adapter errors
**Solution**:
- Verify `@sveltejs/adapter-node` is in package.json devDependencies
- Run `bun install` locally to update bun.lock
- Push updated bun.lock to trigger rebuild

**Problem**: 404 errors on page refresh
**Solution**:
- This is expected with SvelteKit adapter-node
- Railway serves all routes through index.js
- Check svelte.config.js uses adapter-node correctly

## Monitoring & Logs

### View Logs
1. Railway Dashboard → Select Service
2. Click "Deployments" tab
3. Click on a deployment to view logs
4. Or use CLI: `railway logs`

### Metrics
Railway provides automatic monitoring:
- **CPU Usage**: View in service dashboard
- **Memory Usage**: View in service dashboard
- **Network**: Request/response metrics
- **Deployments**: Success/failure history

### Health Checks
Both services expose health check endpoints:
- Backend: `GET /health`
- Backend: `GET /` (returns version info)

Set up external monitoring (e.g., UptimeRobot) to ping these endpoints.

## Cost Optimization

**Railway Pricing** (as of 2025):
- **Free Tier**: $5 credit/month
- **Hobby Plan**: $5/month for additional resources
- **Pro Plan**: $20/month for production features

**Estimated Usage for SpendSense:**
- Backend: ~0.5 GB RAM, minimal CPU (demo traffic)
- Frontend: ~0.5 GB RAM, minimal CPU (demo traffic)
- Total: ~1 GB RAM, ~$3-5/month

**Tips to Minimize Costs:**
1. Use free tier for demos/development
2. Sleep services when not in use (Railway Hobby plan feature)
3. Use SQLite instead of PostgreSQL for demos (saves database costs)
4. Monitor usage in Railway dashboard

## Security Considerations

⚠️  **Important Security Notes:**

1. **No Authentication**: Current implementation has no user authentication
   - OK for demo/portfolio
   - Add auth (e.g., Clerk, Auth0) for production

2. **SQLite Security**: Database file is world-readable on Railway
   - Use PostgreSQL for production
   - Enable Railway private networking if available

3. **Environment Variables**: Sensitive data should use Railway secrets
   - API keys should not be in code
   - Use Railway's encrypted environment variables

4. **CORS**: Only add trusted frontend URLs to `CORS_ORIGINS_EXTRA`
   - Don't use wildcard `*` in production

## Next Steps After Deployment

1. **Test All Features**:
   - Dashboard page loads with account data
   - Transactions page shows full history
   - Insights page displays personalized recommendations
   - Operator view shows decision traceability

2. **Load Synthetic Data** (if needed):
   ```bash
   railway run --service spendsense-backend uv run python scripts/init_and_load_data.py
   ```

3. **Set Up Monitoring**:
   - Add external uptime monitor
   - Set up error tracking (e.g., Sentry)
   - Monitor Railway usage dashboard

4. **Custom Domain** (Optional):
   - Railway → Service → Settings → Networking
   - Add custom domain
   - Update DNS records
   - Update environment variables with new domain

5. **Continuous Deployment**:
   - Push to main/master branch triggers auto-deploy
   - Railway → Service → Settings → Source
   - Configure branch to deploy from

## Validation Checklist

Before going live, verify:

- [ ] Backend health endpoint returns 200 OK
- [ ] Backend API docs accessible at `/docs`
- [ ] Frontend loads without errors
- [ ] CORS is configured correctly (no CORS errors in browser console)
- [ ] Database initialized with synthetic users
- [ ] All pages load (Dashboard, Transactions, Insights, Operator)
- [ ] User dropdown shows multiple users
- [ ] Switching users updates data correctly
- [ ] Insights page shows personalized recommendations
- [ ] No 500 errors in Railway logs
- [ ] Environment variables set correctly on both services

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **SvelteKit Adapters**: https://kit.svelte.dev/docs/adapters
- **Project Documentation**: See `RAILWAY_DEPLOYMENT.md` for detailed guide

---

✅ **Deployment Status**: Ready
📝 **Last Validated**: 2025-11-09
🔧 **Critical Fixes**: All applied
🚀 **Ready to Deploy**: Yes
