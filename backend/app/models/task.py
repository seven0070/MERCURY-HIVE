from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    creator_id = Column(String, ForeignKey("agents.id"), nullable=False)
    assigned_to_id = Column(String, ForeignKey("agents.id"), nullable=True)

    status = Column(String, nullable=False, default="Created")
    priority = Column(String, default="Normal")

    context_memory_ids = Column(Text, nullable=True)
    allowed_tools = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class TaskResult(Base):
    __tablename__ = "task_results"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)

    status = Column(String, nullable=False)
    output_data = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
