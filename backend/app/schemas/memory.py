from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class MemoryEntryBase(BaseModel):
    content: str
    department_id: Optional[str] = None
    visibility: Optional[str] = "private"

class MemoryEntryCreate(MemoryEntryBase):
    pass

class MemoryEntryUpdate(BaseModel):
    content: str
    resolve_conflict_id: Optional[str] = None

class MemoryEntryResponse(MemoryEntryBase):
    id: str
    agent_id: str
    version: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MemoryConflictResponse(BaseModel):
    id: str
    memory_id: str
    agent_id: str
    proposed_content: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
