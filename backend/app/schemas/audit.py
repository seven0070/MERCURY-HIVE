from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditEventBase(BaseModel):
    actor_id: str
    action: str
    target_resource: Optional[str] = None
    result: str
    reason: Optional[str] = None
    metadata_json: Optional[str] = None

class AuditEventCreate(AuditEventBase):
    pass

class AuditEventResponse(AuditEventBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
