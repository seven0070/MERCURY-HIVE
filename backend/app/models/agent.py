from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    display_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Owner, CEO, HR, Department Manager, Worker, Temporary Sub-Agent
    department = Column(String, nullable=True)
    manager_id = Column(String, ForeignKey("agents.id"), nullable=True)
    status = Column(String, nullable=False, default="Proposed") # Proposed, Sandbox, Active, Probation, Restricted, Suspended, Quarantined, Archived, Terminated
    allowed_tools = Column(Text, nullable=True) # JSON string
    memory_scope = Column(String, nullable=True)
    authority_scope = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(String, ForeignKey("agents.id"), nullable=True)

    manager = relationship("Agent", remote_side=[id], foreign_keys=[manager_id], backref="subordinates")
    parent = relationship("Agent", remote_side=[id], foreign_keys=[parent_id], backref="children")
