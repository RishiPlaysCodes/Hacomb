"""
VIGIL LABS - Execution Schemas
Pydantic models for tool execution requests/responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExecuteToolRequest(BaseModel):
    tool_id: str
    arguments: Dict[str, Any] = {}
    working_directory: Optional[str] = None
    timeout: Optional[int] = None
    notes: Optional[str] = None
    tags: List[str] = []


class ExecutionResponse(BaseModel):
    id: str
    tool_id: str
    user_id: str
    command: str
    arguments_used: dict = {}
    status: str
    pid: Optional[int] = None
    exit_code: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    output_file: Optional[str] = None
    report_path: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    is_favorite: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    executions: List[ExecutionResponse]
    total: int
    page: int
    per_page: int


class StopExecutionRequest(BaseModel):
    execution_id: str
    force: bool = False


class PresetCreate(BaseModel):
    tool_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    arguments: Dict[str, Any] = {}
    is_default: bool = False


class PresetResponse(BaseModel):
    id: str
    tool_id: str
    name: str
    description: Optional[str] = None
    arguments: dict = {}
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True
