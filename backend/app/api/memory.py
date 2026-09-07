from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.memory import MemoryEntryCreate, MemoryEntryUpdate, MemoryEntryResponse
from app.security.permissions import require_permission
from app.models.agent import Agent
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])

@router.post("/", response_model=MemoryEntryResponse)
def create_memory(memory_in: MemoryEntryCreate, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("access_memory_api"))):
    svc = MemoryService(db, current_user)
    return svc.create_memory(memory_in)

@router.get("/search", response_model=list[MemoryEntryResponse])
def search_memory(q: str = Query(...), db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("access_memory_api"))):
    svc = MemoryService(db, current_user)
    return svc.search_memory(q)

@router.get("/{memory_id}", response_model=MemoryEntryResponse)
def get_memory(memory_id: str, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("access_memory_api"))):
    svc = MemoryService(db, current_user)
    return svc.read_memory(memory_id)

@router.put("/{memory_id}", response_model=MemoryEntryResponse)
def update_memory(memory_id: str, memory_in: MemoryEntryUpdate, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("access_memory_api"))):
    svc = MemoryService(db, current_user)
    return svc.update_memory(memory_id, memory_in)
