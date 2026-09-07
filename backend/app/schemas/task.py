from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str
    department_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    status: Optional[str] = "Created"
    priority: Optional[str] = "Normal"
    context_memory_ids: Optional[str] = None
    allowed_tools: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    context_memory_ids: Optional[str] = None
    allowed_tools: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class TaskResultCreate(BaseModel):
    status: str
    output_data: Optional[str] = None
    error_details: Optional[str] = None

class TaskResultResponse(TaskResultCreate):
    id: str
    task_id: str
    agent_id: str
    created_at: datetime
    class Config:
        from_attributes = True
