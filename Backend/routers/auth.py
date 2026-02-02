"""Authentication router - login, register, and user management."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from core.auth import CurrentUser
from core.security import create_access_token, get_password_hash, verify_password
from db.database import DbSession
from models.user import User
from schema.user import (
    PasswordChange,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: DbSession) -> Token:
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 6 characters
    - **name**: Optional display name
    """
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        auth_provider="local",
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    
    # Generate access token
    access_token = create_access_token(subject=new_user.id)
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: DbSession) -> Token:
    """
    Authenticate user and return access token.
    
    - **email**: Registered email address
    - **password**: Account password
    """
    # Find user by email
    stmt = select(User).where(User.email == credentials.email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    
    logger.info(f"User logged in: {user.email}")
    
    # Generate access token
    access_token = create_access_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get the current authenticated user's information."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    """Update the current user's profile."""
    if user_update.name is not None:
        current_user.name = user_update.name
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentUser,
    db: DbSession,
) -> dict[str, str]:
    """Change the current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password updated successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: CurrentUser) -> dict[str, str]:
    """
    Logout the current user.
    
    Note: Since we use stateless JWT tokens, this is mainly for client-side
    token cleanup. The client should discard the token.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}
