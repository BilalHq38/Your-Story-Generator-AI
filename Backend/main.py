"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import register_exception_handlers
from core.logging import setup_logging
from db.database import init_db
from routers import jobs_router, story_router, tts_router


# Configure logging before app starts
setup_logging(
    level=settings.log_level,
    format_style="detailed" if settings.is_development else "json",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.
    
    Startup: Initialize database, warm up connections
    Shutdown: Clean up resources
    """
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")
    
    if settings.is_development:
        # Only auto-create tables in development
        # Production should use Alembic migrations
        init_db()
        logger.info("Database tables initialized")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description="An API for creating and managing choose-your-own-adventure stories powered by AI.",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Register exception handlers
register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ============ Include Routers ============

app.include_router(story_router, prefix=settings.api_prefix)
app.include_router(tts_router, prefix=settings.api_prefix)
app.include_router(jobs_router, prefix=settings.api_prefix)


# ============ Health & Root Endpoints ============


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    response_model=dict,
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns:
        Health status and basic info
    """
    from sqlalchemy import text
    from db.database import SessionLocal
    
    # Check database connectivity
    db_healthy = True
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_healthy else "unhealthy",
            "version": settings.api_version,
            "environment": settings.environment,
            "database": "connected" if db_healthy else "disconnected",
        },
    )


@app.get(
    "/health/ready",
    tags=["health"],
    summary="Readiness check",
)
async def readiness_check() -> dict[str, str]:
    """Readiness probe - returns 200 when app is ready to serve traffic."""
    return {"status": "ready"}


@app.get(
    "/health/live",
    tags=["health"],
    summary="Liveness check",
)
async def liveness_check() -> dict[str, str]:
    """Liveness probe - returns 200 when app is alive."""
    return {"status": "alive"}


# ============ Run with Uvicorn ============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
