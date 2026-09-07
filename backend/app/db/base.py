from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic
from app.models.agent import Agent
from app.models.audit import AuditEvent
from app.models.department import Department, CrossDepartmentBridge
from app.models.memory import MemoryEntry, MemoryVersion, MemoryShare, MemoryConflict
from app.models.message import AgentMessage
from app.models.task import Task, TaskResult
