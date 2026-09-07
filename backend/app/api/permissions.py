from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.services import agent_service
from app.security.permissions import evaluate_permission
from app.models.agent import Agent

router = APIRouter(prefix="/permissions", tags=["permissions"])

def get_current_actor(actor_id: str = Header(...), db: Session = Depends(get_db)):
    actor = agent_service.get_agent(db, actor_id)
    if not actor:
        raise HTTPException(status_code=401, detail="Invalid actor_id")
    return actor

@router.get("/check")
def check_permission(action: str, target_id: Optional[str] = None, resource: Optional[str] = None, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    target = None
    if target_id:
        target = agent_service.get_agent(db, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Target agent not found")

    is_allowed = evaluate_permission(db, actor, action, target=target, resource=resource)
    return {"allowed": is_allowed}
