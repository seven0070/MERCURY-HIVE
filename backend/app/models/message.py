from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    sender_id = Column(String, ForeignKey("agents.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("agents.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)

    message_type = Column(String, nullable=False, default="Direct")
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
