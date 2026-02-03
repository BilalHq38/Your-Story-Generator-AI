"""
Security utilities for password hashing and JWT tokens.
Production-safe for Vercel.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from core.config import settings


# -------------------------
# Password hashing
# -------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicit cost for consistency
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)


# -------------------------
# JWT
# -------------------------
def create_access_token(
    subject: int | str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.
    """

    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY is not configured")

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode = {
        "sub": str(subject),
        "iat": now,     # Issued at
        "exp": expire,  # Expiration
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt
