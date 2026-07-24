"""
VIGIL LABS - Auth Schemas
Pydantic models for authentication requests/responses with strict validation.
"""
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    
    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Ensure username contains only safe characters."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError("Username must start with a letter and contain only letters, numbers, underscores, and hyphens")
        return v


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    email: Optional[str] = Field(None, max_length=254)
    display_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Ensure username contains only safe characters."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError("Username must start with a letter and contain only letters, numbers, underscores, and hyphens")
        return v
    
    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator("display_name")
    @classmethod
    def sanitize_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Remove potentially dangerous characters from display name."""
        if v is None:
            return v
        # Remove control characters and null bytes
        v = re.sub(r'[\x00-\x1f\x7f]', '', v)
        # Remove HTML tags
        v = re.sub(r'<[^>]*>', '', v)
        return v.strip()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


TokenResponse.model_rebuild()
