"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, computed_field


class UserCreate(BaseModel):
    """Schema for user registration."""
    
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (public data)."""
    
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    @computed_field
    @property
    def username(self) -> str:
        """Return name or email prefix as username."""
        if self.name:
            return self.name
        return self.email.split('@')[0] if self.email else 'user'
    
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    name: Optional[str] = Field(None, max_length=255)


class PasswordChange(BaseModel):
    """Schema for changing password."""
    
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for decoded token data."""
    
    user_id: Optional[int] = None
