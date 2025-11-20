"""
QEW Innovation Corridor - Main API Gateway
===========================================

FastAPI backend for work zone safety system.
Handles camera management, AI analysis, and work zone detection.

Author: ADBA Labs
Project: QEW Innovation Corridor
Phase: Comprehensive Backend Refactor
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from config import settings
from database import init_db, close_db

# Import API routers
from api import cameras, work_zones, collection, directions, analysis

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler

    Runs on startup and shutdown to manage resources.
    """
    # Startup
    logger.info("🚀 Starting QEW Innovation Corridor API Gateway...")
    logger.info(f"Environment: {settings.LOG_LEVEL}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    logger.info(f"GCP Bucket: {settings.GCP_STORAGE_BUCKET}")
    logger.info(f"vRSU Service: {settings.VRSU_SERVICE_URL}")

    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue anyway for health checks

    yield

    # Shutdown
    logger.info("🛑 Shutting down QEW Innovation Corridor API Gateway...")
    await close_db()
    logger.info("✅ Cleanup complete")


# Initialize FastAPI app
app = FastAPI(
    title="QEW Innovation Corridor API",
    description="AI-powered work zone safety analysis system for Ontario QEW corridor",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "details": str(exc) if settings.LOG_LEVEL == "DEBUG" else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "QEW Innovation Corridor API Gateway",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/api/docs",
        "endpoints": {
            "cameras": "/api/cameras",
            "work_zones": "/api/work-zones",
            "collection": "/api/collection",
            "directions": "/api/directions",
            "analysis": "/api/analysis"
        }
    }


@app.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint for monitoring

    Returns:
        Service health status and configuration
    """
    try:
        # TODO: Add database ping check
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": db_status,
        "gcp_bucket": settings.GCP_STORAGE_BUCKET,
        "vrsu_enabled": settings.VRSU_ENABLED,
        "features": {
            "rate_limiting": settings.ENABLE_RATE_LIMITING,
            "caching": settings.ENABLE_CACHING,
            "analytics": settings.ENABLE_ANALYTICS
        }
    }


# Include API routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["Cameras"])
app.include_router(work_zones.router, prefix="/api/work-zones", tags=["Work Zones"])
app.include_router(collection.router, prefix="/api/collection", tags=["Collection"])
app.include_router(directions.router, prefix="/api/directions", tags=["Directions"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])


if __name__ == "__main__":
    # Run with: python main.py
    # For production, use: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
