"""
User database model for authentication.
Production-safe for FastAPI + Neon + Vercel.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.database import Base


class User(Base):
    """User model for authentication (password + OAuth)."""

    __tablename__ = "users"
    __table_args__ = (
        # Ensure one account per OAuth provider identity
        UniqueConstraint(
            "auth_provider",
            "provider_id",
            name="uq_users_auth_provider_id",
        ),
        Index("ix_users_auth_provider", "auth_provider"),
        Index("ix_users_provider_id", "provider_id"),
    )

    # -------------------------
    # Identity
    # -------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[Optional[str]] = mapped_column(String(255))

    picture: Mapped[Optional[str]] = mapped_column(String(500))

    # -------------------------
    # Authentication
    # -------------------------
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,  # NULL allowed ONLY for OAuth users
    )

    auth_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,  # e.g. "google", "github"
    )

    provider_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # -------------------------
    # Status
    # -------------------------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # -------------------------
    # Timestamps
    # -------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
    )

    # -------------------------
    # Helpers
    # -------------------------
    @property
    def username(self) -> str:
        """
        Stable username for display.
        """
        if self.name and self.name.strip():
            return self.name.strip()
        return self.email.split("@")[0]

    @property
    def is_oauth_user(self) -> bool:
        return bool(self.auth_provider and self.provider_id)

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"email='{self.email}' "
            f"provider={self.auth_provider}>"
        )
