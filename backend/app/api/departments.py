from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.department import Department, CrossDepartmentBridge
from app.schemas.department import DepartmentCreate, DepartmentResponse, CrossDepartmentBridgeCreate, CrossDepartmentBridgeResponse
from app.security.permissions import require_permission
from app.models.agent import Agent

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentResponse)
def create_department(department_in: DepartmentCreate, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("manage_departments"))):
    department = Department(**department_in.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.post("/bridge", response_model=CrossDepartmentBridgeResponse)
def create_bridge(bridge_in: CrossDepartmentBridgeCreate, db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("create_bridge"))):
    bridge = CrossDepartmentBridge(**bridge_in.model_dump(), approved_by_id=current_user.id)
    db.add(bridge)
    db.commit()
    db.refresh(bridge)
    return bridge

@router.get("/", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), current_user: Agent = Depends(require_permission("view_departments"))):
    return db.query(Department).all()
