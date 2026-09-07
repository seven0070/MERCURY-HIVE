from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.gateway import GatewayRequest, GatewayResponse
from app.services.model_gateway import gateway
from app.security.permissions import require_permission
from app.models.agent import Agent

router = APIRouter(prefix="/gateway", tags=["gateway"])

@router.post("/generate", response_model=GatewayResponse)
def generate_response(request: GatewayRequest, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("use_model_gateway"))):
    """
    Direct access to the model gateway, protected by permission.
    Normally, agents use AgentRuntime.execute_agent_step, but this allows direct API access if authorized.
    """
    try:
        return gateway.generate_response(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
