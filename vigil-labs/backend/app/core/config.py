"""
VIGIL LABS - Core Configuration
Central configuration management with environment variable support.
"""
import os
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VIGIL LABS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INACTIVITY_TIMEOUT_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./vigil_labs.db"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TOOLS_DIR: Path = BASE_DIR / "tools"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    
    # Execution
    DEFAULT_TIMEOUT: int = 300  # 5 minutes
    MAX_TIMEOUT: int = 3600  # 1 hour
    MAX_CONCURRENT_PROCESSES: int = 10
    
    # AI Assistant
    AI_ENABLED: bool = True
    AI_MODEL: str = "local"
    
    # Cross-platform
    PLATFORM: str = os.name  # 'nt' for Windows, 'posix' for Linux/Mac
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure directories exist
for dir_path in [settings.TOOLS_DIR, settings.REPORTS_DIR, settings.LOGS_DIR, settings.EXPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
