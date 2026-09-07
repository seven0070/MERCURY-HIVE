from sqlalchemy.orm import Session
from app.models.memory import MemoryEntry, MemoryVersion, MemoryShare, MemoryConflict
from app.schemas.memory import MemoryEntryCreate, MemoryEntryUpdate
from app.models.agent import Agent
from app.security.permissions import evaluate_permission
from fastapi import HTTPException
from datetime import datetime

class MemoryService:
    def __init__(self, db: Session, actor: Agent):
        self.db = db
        self.actor = actor

    def create_memory(self, memory_in: MemoryEntryCreate) -> MemoryEntry:
        # Visibility checks handled in permission evaluation (write_memory)
        if memory_in.visibility not in ["private", "department", "global"]:
            raise HTTPException(status_code=400, detail="Invalid visibility scope")

        memory = MemoryEntry(**memory_in.model_dump(), agent_id=self.actor.id)
        if memory_in.department_id is None:
             memory.department_id = getattr(self.actor, 'department_id', None)

        # We need a target object to evaluate permission against
        if not evaluate_permission(self.db, self.actor, "write_memory", target=memory):
             raise HTTPException(status_code=403, detail="Permission denied to create memory with this scope")

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def update_memory(self, memory_id: str, memory_in: MemoryEntryUpdate) -> MemoryEntry:
        memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
        if not memory:
             raise HTTPException(status_code=404, detail="Memory not found")

        if not evaluate_permission(self.db, self.actor, "write_memory", target=memory):
             # If they can't write directly, they can propose a conflict
             conflict = MemoryConflict(memory_id=memory.id, agent_id=self.actor.id, proposed_content=memory_in.content)
             self.db.add(conflict)
             self.db.commit()
             raise HTTPException(status_code=403, detail="Write permission denied. Conflict proposed.")

        if memory_in.resolve_conflict_id:
             conflict = self.db.query(MemoryConflict).filter(MemoryConflict.id == memory_in.resolve_conflict_id).first()
             if conflict:
                  conflict.status = "resolved"

        # Save old version
        old_version = MemoryVersion(memory_id=memory.id, content=memory.content, version=memory.version)
        self.db.add(old_version)

        memory.content = memory_in.content
        memory.version += 1
        memory.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def read_memory(self, memory_id: str) -> MemoryEntry:
        memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        if not evaluate_permission(self.db, self.actor, "read_memory", target=memory):
             raise HTTPException(status_code=403, detail="Permission denied to read this memory")
        return memory

    def search_memory(self, query: str) -> list[MemoryEntry]:
        # Simple DB like/ilike search placeholder. In reality this calls an embedding DB.
        memories = self.db.query(MemoryEntry).filter(MemoryEntry.content.ilike(f"%{query}%")).all()
        return [m for m in memories if evaluate_permission(self.db, self.actor, "read_memory", target=m)]
