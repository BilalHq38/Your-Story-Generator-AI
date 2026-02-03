"""
User schemas for API requests and responses.
Production-safe for FastAPI + Pydantic v2.
"""

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    computed_field,
)


# =====================================================
# Requests
# =====================================================

class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = Field(None, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> EmailStr:
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Password cannot be only numbers")
        if v.lower() in {"password", "12345678", "qwerty"}:
            raise ValueError("Password is too weak")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> EmailStr:
        return v.lower()


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    name: Optional[str] = Field(None, max_length=255)


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# =====================================================
# Responses
# =====================================================

class UserResponse(BaseModel):
    """Schema for user response (public data)."""

    model_config = {"from_attributes": True}

    id: int
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    @computed_field(return_type=str)
    @property
    def username(self) -> str:
        """
        Stable display username.
        """
        if self.name and self.name.strip():
            return self.name.strip()
        return self.email.split("@")[0]


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """
    Schema for decoded JWT token data.
    Mirrors JWT payload.
    """

    sub: Optional[str] = None  # user_id as string
