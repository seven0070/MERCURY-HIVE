from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.agent import Agent
from app.security.permissions import require_permission
from app.services.orchestrator import TaskOrchestrator

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

class OrchestrateRequest(BaseModel):
    title: str
    description: str
    department_id: str = None

class OrchestrateResponse(BaseModel):
    status: str
    detail: str

@router.post("/execute", response_model=OrchestrateResponse)
def execute_orchestration(
    req: OrchestrateRequest,
    db: Session = Depends(get_db),
    current_user: Agent = Depends(require_permission("orchestrate_tasks"))
):
    try:
        orchestrator = TaskOrchestrator(db, current_user)
        result = orchestrator.orchestrate_task(title=req.title, description=req.description, target_department_id=req.department_id)
        status = "Failed" if "ESCALATION" in result else "Success"
        return OrchestrateResponse(status=status, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
