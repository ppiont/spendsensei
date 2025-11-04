"""SpendSense FastAPI application entry point"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from spendsense.database import init_db
from spendsense.config import settings
from spendsense.routers import users_router, accounts_router, transactions_router, insights_router

# Set up logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Register routers
app.include_router(users_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(insights_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a generic 500 response to avoid
    exposing internal error details to clients.
    """
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later."
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    logger.info("Starting up SpendSense API...")
    await init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Hello SpendSense", "version": settings.api_version}


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "service": "spendsense-api"}
