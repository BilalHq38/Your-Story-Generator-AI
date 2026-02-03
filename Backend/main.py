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
from db.database import init_db, SessionLocal
from routers.auth import router as auth_router
from routers.story import router as story_router
from routers.jobs import router as jobs_router
from routers.tts import router as tts_router


# -------------------------------------------------
# Logging
# -------------------------------------------------
setup_logging(
    level=settings.log_level,
    format_style="detailed" if settings.is_development else "json",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------
# Lifespan (SAFE for serverless)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")

    # Only auto-create tables for SQLite in development
    if settings.is_development and settings.database_url.startswith("sqlite"):
        try:
            init_db()
            logger.info("Database tables initialized (SQLite)")
        except Exception as e:
            logger.error(f"Database init failed: {e}")

    # DO NOT pre-warm heavy services in production (serverless)
    if settings.is_development:
        try:
            from core.story_generator import get_story_generator
            get_story_generator()
            logger.info("Story generator pre-warmed")
        except Exception as e:
            logger.warning(f"Story generator pre-warm skipped: {e}")

    logger.info("Application startup complete")
    yield
    logger.info("Application shutting down...")


# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(
    title=settings.api_title,
    description="Choose-your-own-adventure stories powered by AI.",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    redirect_slashes=True,
)


# -------------------------------------------------
# Exception handlers
# -------------------------------------------------
register_exception_handlers(app)


# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(story_router, prefix=settings.api_prefix)
app.include_router(tts_router, prefix=settings.api_prefix)
app.include_router(jobs_router, prefix=settings.api_prefix)


# -------------------------------------------------
# Root & Health
# -------------------------------------------------
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }

# -------------------------------------------------
# Public test endpoint (for auth debugging)
# -------------------------------------------------
@app.get("/__public_test")
async def public_test():
    return {"ok": True}


@app.get("/health", tags=["health"])
async def health_check() -> JSONResponse:
    from sqlalchemy import text

    db_healthy = True
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False

    return JSONResponse(
        status_code=status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if db_healthy else "unhealthy",
            "environment": settings.environment,
            "database": "connected" if db_healthy else "disconnected",
        },
    )


@app.get("/health/ready", tags=["health"])
async def readiness_check() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/health/live", tags=["health"])
async def liveness_check() -> dict[str, str]:
    return {"status": "alive"}


# -------------------------------------------------
# Local run (ignored by Vercel)
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
