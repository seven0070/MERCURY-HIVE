from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.audit import AuditEventResponse
from app.audit import service as audit_service
from app.security.permissions import evaluate_permission
from app.services import agent_service
from app.models.agent import Agent

router = APIRouter(prefix="/audit", tags=["audit"])

def get_current_actor(actor_id: str = Header(...), db: Session = Depends(get_db)):
    actor = agent_service.get_agent(db, actor_id)
    if not actor:
        raise HTTPException(status_code=401, detail="Invalid actor_id")
    return actor

@router.get("/", response_model=List[AuditEventResponse])
def get_audit_logs(skip: int = 0, limit: int = 100, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    if not evaluate_permission(db, actor, "read_audit"):
        raise HTTPException(status_code=403, detail="Permission denied to read audit logs")
    return audit_service.get_audit_events(db, skip=skip, limit=limit)
