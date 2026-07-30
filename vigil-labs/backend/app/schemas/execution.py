"""
VIGIL LABS - Execution Schemas
Pydantic models for tool execution requests/responses with validation.
"""
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExecuteToolRequest(BaseModel):
    tool_id: str = Field(..., min_length=1, max_length=36)
    arguments: Dict[str, Any] = {}
    working_directory: Optional[str] = Field(None, max_length=500)
    timeout: Optional[int] = Field(None, ge=1, le=3600)
    notes: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default=[], max_length=10)
    
    @field_validator("tool_id")
    @classmethod
    def validate_tool_id(cls, v: str) -> str:
        """Ensure tool_id is a valid UUID format."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(pattern, v.lower()):
            raise ValueError("Invalid tool ID format")
        return v
    
    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, v: Optional[str]) -> Optional[str]:
        """Prevent path traversal in working directory."""
        if v is None:
            return v
        if ".." in v or "\x00" in v:
            raise ValueError("Invalid working directory path")
        return v
    
    @field_validator("arguments")
    @classmethod
    def validate_arguments_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Limit argument count and value sizes."""
        if len(v) > 50:
            raise ValueError("Too many arguments (max 50)")
        for key, value in v.items():
            if isinstance(value, str) and len(value) > 10000:
                raise ValueError(f"Argument '{key}' value too long (max 10000 chars)")
        return v
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Sanitize tags."""
        return [re.sub(r'[^a-zA-Z0-9_-]', '', tag)[:50] for tag in v[:10]]


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
    execution_id: str = Field(..., min_length=1, max_length=36)
    force: bool = False
    
    @field_validator("execution_id")
    @classmethod
    def validate_execution_id(cls, v: str) -> str:
        """Ensure execution_id is a valid UUID format."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(pattern, v.lower()):
            raise ValueError("Invalid execution ID format")
        return v


class PresetCreate(BaseModel):
    tool_id: str = Field(..., min_length=1, max_length=36)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    arguments: Dict[str, Any] = {}
    is_default: bool = False
    
    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Remove dangerous characters from preset name."""
        v = re.sub(r'[<>"\x00-\x1f]', '', v)
        return v.strip()


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
