from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services import agent_service
from app.security.permissions import evaluate_permission
from app.models.agent import Agent

router = APIRouter(prefix="/agents", tags=["agents"])

def get_current_actor(actor_id: str = Header(...), db: Session = Depends(get_db)):
    actor = agent_service.get_agent(db, actor_id)
    if not actor:
        raise HTTPException(status_code=401, detail="Invalid actor_id")
    return actor

@router.post("/", response_model=AgentResponse)
def create_agent(agent_in: AgentCreate, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    return agent_service.register_agent(db, agent_in, actor)

@router.get("/", response_model=List[AgentResponse])
def list_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Assuming listing is open for now, can add permission check if needed
    return agent_service.get_agents(db, skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=AgentResponse)
def read_agent(agent_id: str, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    target = agent_service.get_agent(db, agent_id)
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not evaluate_permission(db, actor, "read_agent", target=target):
        raise HTTPException(status_code=403, detail="Permission denied to read this agent")
    return target

@router.put("/{agent_id}/status", response_model=AgentResponse)
def update_agent_status(agent_id: str, new_status: str, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    return agent_service.change_status(db, agent_id, new_status, actor)
