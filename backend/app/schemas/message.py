from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AgentMessageBase(BaseModel):
    receiver_id: Optional[str] = None
    department_id: Optional[str] = None
    task_id: Optional[str] = None
    message_type: Optional[str] = "Direct"
    content: str

class AgentMessageCreate(AgentMessageBase):
    pass

class AgentMessageResponse(AgentMessageBase):
    id: str
    sender_id: str
    created_at: datetime
    read_at: Optional[datetime] = None
    class Config:
        from_attributes = True
