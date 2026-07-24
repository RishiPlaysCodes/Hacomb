"""
VIGIL LABS - Custom Exception Classes
Structured exception hierarchy for consistent API error responses.
"""
from typing import Optional, List, Dict, Any


class VigilLabsError(Exception):
    """Base exception for all VIGIL LABS errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to API response format."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


class ValidationError(VigilLabsError):
    """Input validation failed."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"errors": errors or []},
        )


class AuthenticationError(VigilLabsError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(VigilLabsError):
    """Authorization/permission denied."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundError(VigilLabsError):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} '{identifier}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class ConflictError(VigilLabsError):
    """Resource conflict (duplicate, already exists, etc.)."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )


class RateLimitError(VigilLabsError):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Too many requests. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after},
        )


class ExecutionError(VigilLabsError):
    """Tool execution failed."""
    
    def __init__(self, message: str, command: str = "", exit_code: Optional[int] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="EXECUTION_ERROR",
            details={"command": command, "exit_code": exit_code},
        )


class CommandSecurityError(VigilLabsError):
    """Command failed security validation."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="COMMAND_SECURITY_ERROR",
        )


class ServiceUnavailableError(VigilLabsError):
    """External service or dependency unavailable."""
    
    def __init__(self, service: str):
        super().__init__(
            message=f"Service '{service}' is temporarily unavailable",
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service},
        )
