from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.message import AgentMessageCreate, AgentMessageResponse
from app.services.agent_runtime import get_runtime
from app.models.message import AgentMessage
from app.models.agent import Agent

router = APIRouter(prefix="/messages", tags=["messages"])

from app.services import agent_service
def get_current_actor(x_actor_id: str = Header(...), db: Session = Depends(get_db)):
    actor = agent_service.get_agent(db, x_actor_id)
    if not actor:
        raise HTTPException(status_code=401, detail="Invalid actor_id")
    return actor

@router.post("/", response_model=AgentMessageResponse)
def send_message(message_in: AgentMessageCreate, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    runtime = get_runtime(db, actor)
    return runtime.send_message(message_in)

@router.get("/inbox", response_model=List[AgentMessageResponse])
def get_inbox(skip: int = 0, limit: int = 100, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    return db.query(AgentMessage).filter(AgentMessage.receiver_id == actor.id).order_by(AgentMessage.created_at.desc()).offset(skip).limit(limit).all()
