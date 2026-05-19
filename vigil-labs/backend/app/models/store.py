"""
VIGIL LABS - Tool Store Models
Marketplace/Extension Store for browsing, installing, and managing tools.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, JSON
from app.core.database import Base


class StoreTool(Base):
    __tablename__ = "store_tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identity
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    
    # Classification
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)
    
    # Metadata
    icon = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    license = Column(String(50), nullable=True)
    homepage = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    
    # Risk & Platform
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
    supports_linux = Column(Boolean, default=True)
    supports_windows = Column(Boolean, default=False)
    supports_macos = Column(Boolean, default=False)
    
    # Installation
    install_method = Column(String(50), nullable=False)  # apt, pacman, winget, choco, github, pip, npm, binary, script, manual
    install_command_linux = Column(Text, nullable=True)
    install_command_windows = Column(Text, nullable=True)
    install_command_macos = Column(Text, nullable=True)
    github_repo = Column(String(300), nullable=True)
    binary_url_linux = Column(String(500), nullable=True)
    binary_url_windows = Column(String(500), nullable=True)
    executable_name = Column(String(100), nullable=True)  # Binary name to check if installed
    
    # Dependencies
    dependencies = Column(JSON, default=list)
    system_requirements = Column(JSON, default=dict)
    
    # Tool Configuration Template
    command_template = Column(Text, nullable=True)
    default_arguments = Column(JSON, default=list)  # Pre-configured ToolArgument definitions
    
    # Stats
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Status
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InstalledStoreTool(Base):
    __tablename__ = "installed_store_tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_tool_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Status
    status = Column(String(20), default="installed")  # installed, installing, failed, disabled, updating
    installed_version = Column(String(50), nullable=True)
    is_enabled = Column(Boolean, default=True)
    
    # Paths
    install_path = Column(String(500), nullable=True)
    executable_path = Column(String(500), nullable=True)
    
    # Linked Tool ID (when auto-registered)
    linked_tool_id = Column(String(36), nullable=True)
    
    # Timestamps
    installed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked = Column(DateTime, nullable=True)
