"""
Logging configuration for the application.
Optimized for FastAPI + Vercel.
"""

import logging
import sys
from typing import Literal

from core.config import settings


def setup_logging(
    level: str | None = None,
    format_style: Literal["simple", "detailed", "json"] | None = None,
) -> None:
    """
    Configure application logging.
    """

    # Resolve defaults from settings
    log_level_name = (level or settings.log_level).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Choose format automatically
    if format_style is None:
        format_style = "json" if settings.environment == "production" else "detailed"

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 🚫 DO NOT clear handlers on Vercel
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(handler)
    else:
        handler = root_logger.handlers[0]

    # Formatters
    if format_style == "simple":
        formatter = logging.Formatter(
            "%(levelname)s: %(message)s"
        )

    elif format_style == "json":
        formatter = logging.Formatter(
            '{"time":"%(asctime)s",'
            '"level":"%(levelname)s",'
            '"logger":"%(name)s",'
            '"message":"%(message)s"}'
        )

    else:  # detailed
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    # Reduce noise
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # SQLAlchemy logging
    if settings.db_echo:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialized",
        extra={
            "level": log_level_name,
            "format": format_style,
            "environment": settings.environment,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
