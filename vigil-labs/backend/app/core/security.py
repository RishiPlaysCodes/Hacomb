"""
VIGIL LABS - Security Module
Password hashing, JWT token management, rate limiting, and authentication utilities.
Production-grade security with proper validation and protection.
"""
import time
import logging
import bcrypt as _bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from collections import defaultdict
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger("vigil_labs.security")

security_scheme = HTTPBearer()


# ─── Rate Limiting ────────────────────────────────────────────────────────────

class RateLimiter:
    """In-memory rate limiter. For production, use Redis-based solution."""
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lockouts: Dict[str, float] = {}
    
    def _cleanup(self, key: str, window: int):
        """Remove expired entries."""
        cutoff = time.time() - window
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
    
    def is_rate_limited(self, key: str, max_requests: int, window: int) -> Tuple[bool, int]:
        """
        Check if a key is rate limited.
        Returns (is_limited, remaining_requests).
        """
        # Check lockout
        if key in self._lockouts:
            if time.time() < self._lockouts[key]:
                return True, 0
            else:
                del self._lockouts[key]
        
        self._cleanup(key, window)
        current = len(self._requests[key])
        
        if current >= max_requests:
            return True, 0
        
        return False, max_requests - current
    
    def record_request(self, key: str):
        """Record a request for rate limiting."""
        self._requests[key].append(time.time())
    
    def lockout(self, key: str, duration_seconds: int):
        """Lock out a key for a duration."""
        self._lockouts[key] = time.time() + duration_seconds
    
    def reset(self, key: str):
        """Reset rate limit for a key."""
        self._requests.pop(key, None)
        self._lockouts.pop(key, None)


rate_limiter = RateLimiter()


# ─── Password Security ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly (no passlib)."""
    pwd_bytes = password.encode("utf-8")[:72]  # bcrypt 72-byte limit
    salt = _bcrypt.gensalt(rounds=12)
    return _bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return _bcrypt.checkpw(pwd_bytes, hash_bytes)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets minimum security requirements.
    Returns (is_valid, error_message).
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numeric characters"
    
    return True, ""


# ─── JWT Token Management ────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with proper claims."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with extended expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token with proper error handling."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Validate required claims
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Auth Dependencies ────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Extract and validate current user from JWT token."""
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type - access token required",
        )
    return payload


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Require admin role for the current user."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ─── Request Rate Limiting Dependency ─────────────────────────────────────────

async def check_rate_limit(request: Request):
    """General rate limiting dependency."""
    # Skip rate limiting entirely in development
    if settings.ENVIRONMENT == "development":
        return

    client_ip = request.client.host if request.client else "unknown"
    key = f"general:{client_ip}"
    
    is_limited, remaining = rate_limiter.is_rate_limited(
        key,
        settings.RATE_LIMIT_REQUESTS,
        settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    
    if is_limited:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
        )
    
    rate_limiter.record_request(key)


async def check_auth_rate_limit(request: Request):
    """Stricter rate limiting for authentication endpoints."""
    # Skip rate limiting entirely in development
    if settings.ENVIRONMENT == "development":
        return

    client_ip = request.client.host if request.client else "unknown"
    key = f"auth:{client_ip}"
    
    is_limited, remaining = rate_limiter.is_rate_limited(
        key,
        settings.AUTH_RATE_LIMIT_REQUESTS,
        settings.AUTH_RATE_LIMIT_WINDOW_SECONDS,
    )
    
    if is_limited:
        logger.warning(f"Auth rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(settings.AUTH_RATE_LIMIT_WINDOW_SECONDS)},
        )
    
    rate_limiter.record_request(key)


# ─── Command Security ─────────────────────────────────────────────────────────

def sanitize_command_input(value: str) -> str:
    """Sanitize user input that will be used in command construction."""
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Check for shell injection operators
    if not settings.ALLOW_SHELL_OPERATORS:
        for operator in settings.BLOCKED_SHELL_OPERATORS:
            if operator in value:
                raise ValueError(f"Invalid character sequence in input: '{operator}'")
    
    return value


def validate_command_safety(command: str) -> Tuple[bool, str]:
    """
    Validate a constructed command is safe to execute.
    Returns (is_safe, reason).
    """
    command_lower = command.lower().strip()
    
    # Check against blocked commands
    for blocked in settings.BLOCKED_COMMANDS:
        if blocked.lower() in command_lower:
            return False, f"Blocked dangerous command pattern: {blocked}"
    
    # Check for shell escape attempts
    if not settings.ALLOW_SHELL_OPERATORS:
        for operator in settings.BLOCKED_SHELL_OPERATORS:
            if operator in command:
                return False, f"Shell operator '{operator}' not allowed"
    
    return True, ""
