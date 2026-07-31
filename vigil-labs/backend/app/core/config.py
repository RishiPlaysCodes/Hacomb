"""
VIGIL LABS - Core Configuration
Central configuration management with environment variable support.
Production-ready with validation and secure defaults.
"""
import os
import sys
import logging
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VIGIL LABS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security - SECRET_KEY MUST be set via environment variable in production
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INACTIVITY_TIMEOUT_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    
    # CORS - restrict in production
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # window size
    AUTH_RATE_LIMIT_REQUESTS: int = 5  # login attempts per window
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 300  # 5 minute window
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./vigil_labs.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TOOLS_DIR: Path = BASE_DIR / "tools"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: str = ""  # empty = stdout only
    
    # Execution
    DEFAULT_TIMEOUT: int = 300  # 5 minutes
    MAX_TIMEOUT: int = 3600  # 1 hour
    MAX_CONCURRENT_PROCESSES: int = 10
    MAX_OUTPUT_SIZE: int = 10_000_000  # 10MB max output per process
    
    # Command Execution Security
    BLOCKED_COMMANDS: List[str] = [
        "rm -rf /", "mkfs", "dd if=/dev/zero",
        ":(){:|:&};:", "chmod -R 777 /", "shutdown",
        "reboot", "init 0", "init 6",
    ]
    BLOCKED_SHELL_OPERATORS: List[str] = [
        "&&", "||", ";", "|", "`", "$(", "${",
    ]
    ALLOW_SHELL_OPERATORS: bool = False  # Set True only for trusted environments
    
    # AI Assistant
    AI_ENABLED: bool = True
    AI_MODEL: str = "gemini"  # local = rule-based, gemini = Google Gemini AI
    GEMINI_API_KEY: str = ""  # Get free key: https://aistudio.google.com/apikey
    GEMINI_MODEL: str = "gemini-2.0-flash"  # fast + free
    
    # Cross-platform
    PLATFORM: str = os.name  # 'nt' for Windows, 'posix' for Linux/Mac
    
    # First User Setup
    FIRST_USER_IS_ADMIN: bool = True  # Only first registered user gets admin
    REGISTRATION_ENABLED: bool = True
    REQUIRE_EMAIL_VERIFICATION: bool = False
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn if using default secret key in production."""
        if v == "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR":
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                print(
                    "CRITICAL: SECRET_KEY is not set! "
                    "Set SECRET_KEY environment variable for production.",
                    file=sys.stderr,
                )
                sys.exit(1)
        if len(v) < 32:
            print("WARNING: SECRET_KEY should be at least 32 characters.", file=sys.stderr)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Configure logging
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" if settings.LOG_FORMAT == "text"
    else '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
)
logger = logging.getLogger("vigil_labs")

# Ensure directories exist
for dir_path in [settings.TOOLS_DIR, settings.REPORTS_DIR, settings.LOGS_DIR, settings.EXPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
