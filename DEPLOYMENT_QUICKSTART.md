# Railway Deployment Quick Start

## Before You Deploy

1. **Install frontend dependencies**:
   ```bash
   cd spendsense-frontend
   bun install
   ```
   This installs `@sveltejs/adapter-node` required for Railway deployment.

2. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push
   ```

## Deploy to Railway

### 1. Create Railway Project
- Go to [railway.app](https://railway.app)
- Click "New Project" → "Deploy from GitHub repo"
- Select your `spendsensei` repository

### 2. Deploy Backend Service
- Click "New Service" → "GitHub Repo"
- **Root Directory**: `spendsense-backend`
- Railway will use Railpack (configured in `railway.json`) to auto-detect Python and build
- Railpack will use `uv` based on `pyproject.toml`
- Start command is configured in `railway.json`

### 3. Deploy Frontend Service
- Click "New Service" → "GitHub Repo" (in the same project)
- **Root Directory**: `spendsense-frontend`
- Railway will use Railpack (configured in `railway.json`) to auto-detect Node.js and build
- Railpack will use `bun` based on `bun.lock`
- Start command is configured in `railway.json`

### 4. Configure Environment Variables

**Backend Service**:
- `CORS_ORIGINS_EXTRA`: `https://your-frontend-url.railway.app` (set after frontend deploys)

**Frontend Service**:
- `VITE_API_BASE_URL`: `https://your-backend-url.railway.app`
- `PORT`: Automatically set by Railway

**Important**: After setting `VITE_API_BASE_URL`, you must **rebuild** the frontend service (Vite env vars are embedded at build time).

### 5. Get Your URLs
- Railway provides `.railway.app` domains for each service
- Copy the backend URL → set as `VITE_API_BASE_URL` in frontend
- Copy the frontend URL → set as `CORS_ORIGINS_EXTRA` in backend
- Rebuild frontend after setting `VITE_API_BASE_URL`

## That's It!

Your app should now be live. Check the full guide in `RAILWAY_DEPLOYMENT.md` for troubleshooting and advanced configuration.

