from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CrossDepartmentBridge(Base):
    __tablename__ = "cross_department_bridges"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    source_department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    target_department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    purpose = Column(String, nullable=False)
    approved_by_id = Column(String, ForeignKey("agents.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
