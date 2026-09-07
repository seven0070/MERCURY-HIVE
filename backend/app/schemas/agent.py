from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AgentBase(BaseModel):
    display_name: str
    role: str
    department: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = "Proposed"
    allowed_tools: Optional[str] = None
    memory_scope: Optional[str] = None
    authority_scope: Optional[str] = None
    parent_id: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = None
    allowed_tools: Optional[str] = None
    memory_scope: Optional[str] = None
    authority_scope: Optional[str] = None

class AgentResponse(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
