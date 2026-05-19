"""
VIGIL LABS - Tool Model
Comprehensive tool registry with dynamic argument definitions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class ToolCategory(Base):
    __tablename__ = "tool_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Tool(Base):
    __tablename__ = "tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(String(36), ForeignKey("tool_categories.id"), nullable=True)
    executable_path = Column(String(500), nullable=False)
    command_template = Column(Text, nullable=False)
    
    # OS Support
    supports_linux = Column(Boolean, default=True)
    supports_windows = Column(Boolean, default=False)
    
    # Metadata
    icon = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    version = Column(String(50), nullable=True)
    author = Column(String(100), nullable=True)
    
    # Execution Config
    output_format = Column(String(50), default="text")  # text, json, xml, html
    report_path = Column(String(500), nullable=True)
    execution_timeout = Column(Integer, default=300)
    working_directory = Column(String(500), nullable=True)
    run_as_root = Column(Boolean, default=False)
    
    # Environment
    environment_variables = Column(JSON, default=dict)
    dependencies = Column(JSON, default=list)
    
    # Pre/Post execution
    pre_execution_checks = Column(JSON, default=list)
    post_execution_actions = Column(JSON, default=list)
    
    # Status
    is_installed = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    use_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # User
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    arguments = relationship("ToolArgument", back_populates="tool", cascade="all, delete-orphan")
    category = relationship("ToolCategory", lazy="joined")


class ToolArgument(Base):
    __tablename__ = "tool_arguments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_id = Column(String(36), ForeignKey("tools.id"), nullable=False)
    
    # Basic Info
    name = Column(String(100), nullable=False)
    label = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Field Type
    field_type = Column(String(50), nullable=False)  
    # text, textarea, number, select, checkbox, toggle, file, folder,
    # ip, domain, port, interface, password, url, email,
    # port_range, ip_range, wordlist, payload
    
    # Configuration
    flag = Column(String(50), nullable=True)  # CLI flag e.g. -p, --port
    placeholder = Column(String(200), nullable=True)
    default_value = Column(String(500), nullable=True)
    tooltip = Column(Text, nullable=True)
    example = Column(String(500), nullable=True)
    
    # Validation
    is_required = Column(Boolean, default=False)
    validation_regex = Column(String(500), nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    
    # Options (for select/dropdown)
    options = Column(JSON, default=list)  # [{value, label}]
    
    # Display
    order = Column(Integer, default=0)
    group = Column(String(50), nullable=True)  # For grouping related fields
    width = Column(String(20), default="full")  # full, half, third
    is_advanced = Column(Boolean, default=False)
    depends_on = Column(String(100), nullable=True)  # Conditional display
    
    # Relationships
    tool = relationship("Tool", back_populates="arguments")
