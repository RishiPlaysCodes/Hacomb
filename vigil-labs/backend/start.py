#!/usr/bin/env python3
"""
VIGIL LABS - Production Startup Script
Handles environment validation, logging setup, and server launch.
"""
import os
import sys
import uvicorn

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logging_config import setup_logging


def validate_environment():
    """Validate critical environment settings before startup."""
    errors = []
    
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR":
            errors.append("SECRET_KEY must be set via environment variable")
        if settings.DEBUG:
            errors.append("DEBUG must be False in production")
        if "sqlite" in settings.DATABASE_URL:
            print("WARNING: SQLite is not recommended for production. Use PostgreSQL.")
    
    if errors:
        print("CRITICAL: Environment validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def main():
    """Start the VIGIL LABS server."""
    validate_environment()
    setup_logging()
    
    print(f"\n{'='*60}")
    print(f"  VIGIL LABS v{settings.APP_VERSION}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Host: {settings.HOST}:{settings.PORT}")
    print(f"  Workers: {settings.WORKERS}")
    print(f"  Debug: {settings.DEBUG}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        access_log=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
