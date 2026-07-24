"""
VIGIL LABS - Auth Routes
Authentication endpoints: login, register, refresh, session management.
Production-grade with rate limiting, password validation, and proper role assignment.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, get_current_user,
    validate_password_strength, check_auth_rate_limit, rate_limiter,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    UserResponse, RefreshRequest
)

logger = logging.getLogger("vigil_labs.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    _rate_limit=Depends(check_auth_rate_limit),
):
    """Register a new user account."""
    # Check if registration is enabled
    if not settings.REGISTRATION_ENABLED:
        raise HTTPException(status_code=403, detail="Registration is currently disabled")
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check existing username
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")
    
    # Check existing email if provided
    if request.email:
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already registered")
    
    # Determine role: only first user gets admin
    role = "user"
    if settings.FIRST_USER_IS_ADMIN:
        user_count = await db.execute(select(func.count(User.id)))
        if user_count.scalar() == 0:
            role = "admin"
            logger.info(f"First user '{request.username}' registered as admin")
    
    # Create user
    user = User(
        username=request.username,
        email=request.email,
        display_name=request.display_name or request.username,
        hashed_password=hash_password(request.password),
        role=role,
        is_active=True,
        last_login=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.username} (role={role})")
    
    # Generate tokens
    token_data = {"sub": user.id, "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    _rate_limit=Depends(check_auth_rate_limit),
):
    """Login with username and password."""
    client_ip = req.client.host if req.client else "unknown"
    
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning(f"Failed login attempt for '{request.username}' from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt on disabled account '{request.username}' from {client_ip}")
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Update login time
    user.last_login = datetime.utcnow()
    user.last_activity = datetime.utcnow()
    await db.commit()
    
    # Reset rate limit on successful login
    rate_limiter.reset(f"auth:{client_ip}")
    
    logger.info(f"User '{user.username}' logged in from {client_ip}")
    
    # Generate tokens
    token_data = {"sub": user.id, "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    token_data = {"sub": user.id, "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current user profile."""
    result = await db.execute(select(User).where(User.id == current_user["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update activity
    user.last_activity = datetime.utcnow()
    await db.commit()
    
    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current session."""
    # In production, add token to blacklist here (Redis recommended)
    logger.info(f"User '{current_user.get('username')}' logged out")
    return {"message": "Logged out successfully"}
