"""
VIGIL LABS - Workflow Models
Multi-tool pipeline orchestration.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, JSON
from app.core.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(JSON, nullable=False, default=list)  # [{tool_id, tool_name, order, arguments, pipe_output, condition}]
    
    # Status
    status = Column(String(20), default="idle")  # idle, running, completed, failed, stopped
    last_run = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    
    # Config
    is_favorite = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    status = Column(String(20), default="running")  # running, completed, failed, stopped
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    
    # Results per step
    step_results = Column(JSON, default=list)  # [{step_index, status, stdout, stderr, duration}]
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
