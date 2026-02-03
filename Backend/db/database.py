"""
Database configuration and session management.
Optimized for FastAPI + Neon + Vercel (serverless).
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_engine_args():
    """
    Get SQLAlchemy engine arguments based on environment.
    
    IMPORTANT:
    - Vercel (serverless) MUST use NullPool
    - Connection pooling breaks auth on serverless
    """
    engine_args = {
        "echo": settings.db_echo,
        "pool_pre_ping": True,
    }

    # PostgreSQL (Neon, Supabase, etc.)
    if settings.database_url.startswith("postgresql"):
        engine_args.update({
            "poolclass": NullPool,  # ✅ REQUIRED for Vercel
        })
    else:
        # SQLite (local dev)
        engine_args.update({
            "pool_recycle": 300,
        })

    return engine_args


# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    **get_engine_args()
)


# SQLite-specific: enable foreign keys
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for dependency injection
DbSession = Annotated[Session, Depends(get_db)]


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside FastAPI requests.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    
    ⚠️ Use Alembic for production migrations.
    """
    Base.metadata.create_all(bind=engine)
