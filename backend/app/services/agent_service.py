from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate
from app.security.permissions import evaluate_permission
from fastapi import HTTPException

VALID_STATUSES = ["Proposed", "Sandbox", "Active", "Probation", "Restricted", "Suspended", "Quarantined", "Archived", "Terminated"]

def get_agent(db: Session, agent_id: str):
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Agent).offset(skip).limit(limit).all()

def register_agent(db: Session, agent_in: AgentCreate, actor: Agent):
    if not evaluate_permission(db, actor, "create_agent", resource=agent_in.role):
        raise HTTPException(status_code=403, detail="Permission denied to create agent with this role")

    db_agent = Agent(**agent_in.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def change_status(db: Session, agent_id: str, new_status: str, actor: Agent):
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    target = get_agent(db, agent_id)
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not evaluate_permission(db, actor, "change_status", target=target):
        raise HTTPException(status_code=403, detail="Permission denied to change status of this agent")

    target.status = new_status
    db.commit()
    db.refresh(target)
    return target

def initialize_owner(db: Session):
    """Initializes the owner if it doesn't exist."""
    owner = db.query(Agent).filter(Agent.role == "Owner").first()
    if not owner:
        owner = Agent(
            display_name="System Owner",
            role="Owner",
            status="Active"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
    return owner
