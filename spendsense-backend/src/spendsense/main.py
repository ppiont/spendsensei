"""SpendSense FastAPI application entry point"""

from fastapi import FastAPI
from spendsense.database import init_db

# Create FastAPI application
app = FastAPI(
    title="SpendSense",
    description="Financial behavior analysis platform",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    await init_db()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Hello SpendSense"}


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}
