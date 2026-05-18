"""
VIGIL LABS - Execution Model
Track all tool executions with full logging and reporting.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, JSON
from app.core.database import Base


class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_id = Column(String(36), ForeignKey("tools.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Command
    command = Column(Text, nullable=False)
    arguments_used = Column(JSON, default=dict)
    working_directory = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed, stopped, timeout
    pid = Column(Integer, nullable=True)
    exit_code = Column(Integer, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Output
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    output_file = Column(String(500), nullable=True)
    report_path = Column(String(500), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    is_favorite = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id"), nullable=False)
    
    level = Column(String(20), default="info")  # info, warning, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)
