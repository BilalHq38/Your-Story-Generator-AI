"""Database configuration and session management."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_engine_args():
    """Get engine arguments based on database type."""
    # Base settings
    engine_args = {
        "echo": settings.db_echo,
        "pool_pre_ping": True,  # Verify connections before using
    }
    
    # PostgreSQL-specific settings (for Neon, Supabase, etc.)
    if settings.database_url.startswith("postgresql"):
        engine_args.update({
            "pool_size": 5,
            "max_overflow": 10,
            "pool_recycle": 300,  # Recycle connections after 5 minutes
            "pool_timeout": 30,
            # For serverless (Vercel), use NullPool
            # "poolclass": NullPool,  # Uncomment for serverless
        })
        
        # SSL is handled via sslmode in connection string for Neon
    else:
        # SQLite settings
        engine_args["pool_recycle"] = 300
    
    return engine_args


# Create engine with appropriate settings
engine = create_engine(
    settings.database_url,
    **get_engine_args()
)

# SQLite-specific: Enable foreign keys
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
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
    Context manager for database sessions outside of FastAPI requests.
    
    Usage:
        with get_db_context() as db:
            db.query(...)
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
    """Initialize database tables. Use Alembic for production migrations."""
    Base.metadata.create_all(bind=engine)
