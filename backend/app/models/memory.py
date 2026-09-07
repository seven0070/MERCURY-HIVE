from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class MemoryEntry(Base):
    __tablename__ = "memory_entries"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    content = Column(Text, nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    visibility = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

class MemoryVersion(Base):
    __tablename__ = "memory_versions"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    memory_id = Column(String, ForeignKey("memory_entries.id"), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryShare(Base):
    __tablename__ = "memory_shares"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    memory_id = Column(String, ForeignKey("memory_entries.id"), nullable=False)
    target_agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    target_department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryConflict(Base):
    __tablename__ = "memory_conflicts"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    memory_id = Column(String, ForeignKey("memory_entries.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    proposed_content = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
