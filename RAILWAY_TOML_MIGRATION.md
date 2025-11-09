# Railway Configuration Migration to railway.toml

**Date:** 2025-11-09
**Status:** ✅ Fixed - Ready for Deployment

## Issue

Railway was not deploying properly because:
1. Using outdated `railway.json` format
2. Railway now prefers `railway.toml` (TOML format)
3. Missing explicit nixpacks configuration

## Changes Made

### 1. Backend Configuration

**Created `spendsense-backend/railway.toml`:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Created `spendsense-backend/nixpacks.toml`:**
```toml
# Nixpacks configuration for Railway deployment
[phases.setup]
nixPkgs = ["python313"]

[phases.install]
cmds = [
    "curl -LsSf https://astral.sh/uv/install.sh | sh",
    ". $HOME/.local/bin/env",
    "uv sync"
]

[phases.build]
cmds = ["uv run python scripts/init_db_railway.py"]

[start]
cmd = "uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT"
```

### 2. Frontend Configuration

**Created `spendsense-frontend/railway.toml`:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "node build/index.js"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Created `spendsense-frontend/nixpacks.toml`:**
```toml
# Nixpacks configuration for Railway deployment
[phases.setup]
nixPkgs = ["nodejs_20"]

[phases.install]
cmds = [
    "npm install -g bun",
    "bun install"
]

[phases.build]
cmds = ["bun run build"]

[start]
cmd = "node build/index.js"
```

### 3. Removed Old Files

- ❌ Deleted `spendsense-backend/railway.json`
- ❌ Deleted `spendsense-frontend/railway.json`

## Why railway.toml?

According to Railway's latest documentation:
- **TOML format is preferred** over JSON
- Better readability and maintainability
- Consistent with nixpacks.toml format
- Widely used in modern Railway deployments

## Key Configuration Points

### Backend (Python + uv)
- **Builder**: NIXPACKS (Railway's build system)
- **Python**: 3.13 via nixpkgs
- **Package Manager**: uv (installed via script)
- **Database Init**: Runs init_db_railway.py during build
- **Start Command**: Uses uv to run uvicorn
- **Port**: Binds to `$PORT` environment variable

### Frontend (Node + Bun)
- **Builder**: NIXPACKS
- **Node**: Version 20 via nixpkgs
- **Package Manager**: Bun (installed globally)
- **Build**: Runs `bun run build`
- **Start Command**: Node.js runs the built SSR server
- **Port**: Uses default from SvelteKit adapter

## Deployment Steps

### 1. Push Changes
```bash
git add .
git commit -m "Fix Railway deployment with railway.toml configuration"
git push origin operator
```

### 2. Railway Dashboard

**Backend Service:**
1. Railway will auto-detect `railway.toml` and `nixpacks.toml`
2. Set environment variables:
   - `DATABASE_URL` (optional, defaults to sqlite)
   - `CORS_ORIGINS_EXTRA` (set to frontend URL after frontend deploys)
3. Railway will build using nixpacks configuration
4. Database initialization runs automatically during build

**Frontend Service:**
1. Railway will auto-detect `railway.toml` and `nixpacks.toml`
2. Set environment variables:
   - `VITE_API_BASE_URL` (set to backend URL)
   - `NODE_ENV=production`
3. Railway will install bun, build the app, and start the server

### 3. Verify Deployment

**Check Build Logs:**
- Backend should show: "Installing uv" → "Running uv sync" → "Initializing database"
- Frontend should show: "Installing bun" → "Running bun install" → "Running bun run build"

**Test Endpoints:**
```bash
# Backend health check
curl https://your-backend.up.railway.app/health

# Frontend
curl https://your-frontend.up.railway.app/
```

## Environment Variables Required

### Backend
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto | - | Railway sets automatically |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///data/spendsense.db` | Database connection |
| `CORS_ORIGINS_EXTRA` | Yes | - | Frontend URL (comma-separated) |
| `LOG_LEVEL` | No | `INFO` | Python logging level |

### Frontend
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto | - | Railway sets automatically |
| `VITE_API_BASE_URL` | Yes | - | Backend API URL |
| `NODE_ENV` | No | `production` | Node environment |

## Troubleshooting

### Build Fails with "uv: command not found"
**Solution:** The nixpacks.toml installs uv during the install phase. Check build logs for installation errors.

### Frontend Build Fails
**Solution:** Ensure bun installation succeeded. Check logs for "npm install -g bun" output.

### Database Initialization Fails
**Solution:** Check build logs for init_db_railway.py output. The script is idempotent and safe to re-run.

### Port Binding Issues
**Solution:** Ensure startCommand uses `$PORT` variable. Railway injects this automatically.

## Files Modified

- ✅ Created: `spendsense-backend/railway.toml`
- ✅ Created: `spendsense-backend/nixpacks.toml`
- ✅ Created: `spendsense-frontend/railway.toml`
- ✅ Created: `spendsense-frontend/nixpacks.toml`
- ❌ Deleted: `spendsense-backend/railway.json`
- ❌ Deleted: `spendsense-frontend/railway.json`
- ✅ Updated: All documentation references

## Testing Locally

**Backend:**
```bash
cd spendsense-backend
uv sync
uv run python scripts/init_db_railway.py
uv run uvicorn spendsense.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd spendsense-frontend
bun install
bun run build
node build/index.js
```

## References

- Railway Config Documentation: https://docs.railway.app/reference/config-as-code
- Nixpacks Documentation: https://nixpacks.com/docs
- Railway Python Guide: https://docs.railway.app/guides/python
- Railway Node Guide: https://docs.railway.app/guides/node

---

**Status:** ✅ Ready for Railway Deployment
**Next Step:** Push to GitHub and deploy via Railway Dashboard
