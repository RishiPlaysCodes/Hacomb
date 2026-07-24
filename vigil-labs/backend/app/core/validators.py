"""
VIGIL LABS - Input Validators
Centralized input validation and sanitization for all API inputs.
"""
import re
import os
from typing import Optional
from app.core.exceptions import ValidationError


# ─── Text Sanitization ────────────────────────────────────────────────────────

def sanitize_string(value: str, max_length: int = 500, field_name: str = "input") -> str:
    """Sanitize a string input by removing dangerous characters."""
    if not value:
        return value
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Trim whitespace
    value = value.strip()
    
    # Enforce max length
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} exceeds maximum length of {max_length} characters"
        )
    
    return value


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent SQL injection via LIKE patterns."""
    if not query:
        return query
    
    # Escape SQL LIKE special characters
    query = query.replace("\\", "\\\\")
    query = query.replace("%", "\\%")
    query = query.replace("_", "\\_")
    
    # Remove control characters
    query = re.sub(r'[\x00-\x1f\x7f]', '', query)
    
    # Limit length
    return query[:200]


# ─── Path Validation ──────────────────────────────────────────────────────────

def validate_path(path: str, field_name: str = "path") -> str:
    """Validate a filesystem path is safe (no traversal attacks)."""
    if not path:
        raise ValidationError(f"{field_name} is required")
    
    # Normalize path
    normalized = os.path.normpath(path)
    
    # Check for path traversal
    if ".." in normalized.split(os.sep):
        raise ValidationError(f"{field_name} contains invalid path traversal")
    
    # Check for null bytes
    if "\x00" in path:
        raise ValidationError(f"{field_name} contains invalid characters")
    
    return normalized


def validate_working_directory(directory: Optional[str]) -> Optional[str]:
    """Validate a working directory path exists and is safe."""
    if not directory:
        return None
    
    path = validate_path(directory, "working_directory")
    
    if not os.path.isdir(path):
        raise ValidationError(f"Working directory does not exist: {path}")
    
    # Get real path to resolve any symlinks
    real_path = os.path.realpath(path)
    
    return real_path


# ─── Network Input Validation ─────────────────────────────────────────────────

def validate_ip_address(ip: str, field_name: str = "IP address") -> str:
    """Validate an IPv4 address."""
    # Basic IPv4 pattern
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        # Check CIDR notation
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        if not re.match(cidr_pattern, ip):
            raise ValidationError(f"Invalid {field_name}: {ip}")
    
    # Validate octets
    parts = ip.split('/')[0].split('.')
    for part in parts:
        if int(part) > 255:
            raise ValidationError(f"Invalid {field_name}: octet value > 255")
    
    return ip


def validate_port(port, field_name: str = "port") -> int:
    """Validate a port number."""
    try:
        port_num = int(port)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid {field_name}: must be a number")
    
    if not (1 <= port_num <= 65535):
        raise ValidationError(f"Invalid {field_name}: must be between 1 and 65535")
    
    return port_num


def validate_domain(domain: str, field_name: str = "domain") -> str:
    """Validate a domain name."""
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    if not re.match(pattern, domain):
        raise ValidationError(f"Invalid {field_name}: {domain}")
    
    if len(domain) > 253:
        raise ValidationError(f"{field_name} exceeds maximum length")
    
    return domain.lower()


def validate_url(url: str, field_name: str = "URL") -> str:
    """Validate a URL format."""
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    if not re.match(pattern, url):
        raise ValidationError(f"Invalid {field_name}: must be a valid HTTP/HTTPS URL")
    
    if len(url) > 2000:
        raise ValidationError(f"{field_name} exceeds maximum length")
    
    return url


# ─── ID Validation ────────────────────────────────────────────────────────────

def validate_uuid(value: str, field_name: str = "ID") -> str:
    """Validate a UUID format string."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(pattern, value.lower()):
        raise ValidationError(f"Invalid {field_name}: must be a valid UUID")
    return value


# ─── Username/Email Validation ────────────────────────────────────────────────

def validate_username(username: str) -> str:
    """Validate username format."""
    if not username:
        raise ValidationError("Username is required")
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    
    if len(username) > 50:
        raise ValidationError("Username must not exceed 50 characters")
    
    # Only allow alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )
    
    # Cannot start with a number or special char
    if not username[0].isalpha():
        raise ValidationError("Username must start with a letter")
    
    return username


def validate_email(email: str) -> str:
    """Validate email format."""
    if not email:
        raise ValidationError("Email is required")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 254:
        raise ValidationError("Email exceeds maximum length")
    
    return email.lower()
