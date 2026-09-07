from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    target_resource = Column(String, nullable=True)
    result = Column(String, nullable=False) # e.g. "ALLOW", "DENY"
    reason = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True) # JSON string
