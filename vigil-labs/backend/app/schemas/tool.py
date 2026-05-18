"""
VIGIL LABS - Tool Schemas
Pydantic models for tool management requests/responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ToolArgumentSchema(BaseModel):
    name: str
    label: str
    description: Optional[str] = None
    field_type: str = "text"
    flag: Optional[str] = None
    placeholder: Optional[str] = None
    default_value: Optional[str] = None
    tooltip: Optional[str] = None
    example: Optional[str] = None
    is_required: bool = False
    validation_regex: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    options: List[dict] = []
    order: int = 0
    group: Optional[str] = None
    width: str = "full"
    is_advanced: bool = False
    depends_on: Optional[str] = None


class CreateToolRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: Optional[str] = None
    executable_path: str = Field(..., min_length=1)
    command_template: str = Field(..., min_length=1)
    
    supports_linux: bool = True
    supports_windows: bool = False
    
    icon: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    risk_level: str = "low"
    version: Optional[str] = None
    author: Optional[str] = None
    
    output_format: str = "text"
    report_path: Optional[str] = None
    execution_timeout: int = 300
    working_directory: Optional[str] = None
    run_as_root: bool = False
    
    environment_variables: dict = {}
    dependencies: List[str] = []
    
    pre_execution_checks: List[dict] = []
    post_execution_actions: List[dict] = []
    
    arguments: List[ToolArgumentSchema] = []


class UpdateToolRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    executable_path: Optional[str] = None
    command_template: Optional[str] = None
    supports_linux: Optional[bool] = None
    supports_windows: Optional[bool] = None
    icon: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    risk_level: Optional[str] = None
    execution_timeout: Optional[int] = None
    arguments: Optional[List[ToolArgumentSchema]] = None


class ToolResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    executable_path: str
    command_template: str
    supports_linux: bool
    supports_windows: bool
    icon: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    risk_level: str
    version: Optional[str] = None
    author: Optional[str] = None
    output_format: str
    report_path: Optional[str] = None
    execution_timeout: int
    working_directory: Optional[str] = None
    run_as_root: bool
    environment_variables: dict = {}
    dependencies: List[str] = []
    pre_execution_checks: List[dict] = []
    post_execution_actions: List[dict] = []
    is_installed: bool
    is_favorite: bool
    is_active: bool
    use_count: int
    last_used: Optional[datetime] = None
    arguments: List[ToolArgumentSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tool_count: int = 0

    class Config:
        from_attributes = True
