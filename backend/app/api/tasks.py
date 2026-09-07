from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskResultCreate, TaskResultResponse
from app.services.agent_runtime import get_runtime
from app.models.task import Task, TaskResult
from app.models.agent import Agent

router = APIRouter(prefix="/tasks", tags=["tasks"])

from app.services import agent_service
def get_current_actor(x_actor_id: str = Header(...), db: Session = Depends(get_db)):
    actor = agent_service.get_agent(db, x_actor_id)
    if not actor:
        raise HTTPException(status_code=401, detail="Invalid actor_id")
    return actor

@router.post("/", response_model=TaskResponse)
def create_task(task_in: TaskCreate, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    runtime = get_runtime(db, actor)
    return runtime.create_task(task_in)

@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: str, status: str, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    runtime = get_runtime(db, actor)
    return runtime.update_task_status(task_id, status)

@router.post("/{task_id}/results", response_model=TaskResultResponse)
def submit_task_result(task_id: str, result_in: TaskResultCreate, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    runtime = get_runtime(db, actor)
    return runtime.submit_task_result(task_id, result_in)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != actor.id and task.assigned_to_id != actor.id and actor.role not in ["Owner", "CEO", "HR"]:
        raise HTTPException(status_code=403, detail="Not authorized to view task")
    return task

@router.get("/", response_model=List[TaskResponse])
def list_tasks(skip: int = 0, limit: int = 100, actor: Agent = Depends(get_current_actor), db: Session = Depends(get_db)):
    if actor.role in ["Owner", "CEO", "HR"]:
        return db.query(Task).offset(skip).limit(limit).all()
    return db.query(Task).filter(Task.assigned_to_id == actor.id).offset(skip).limit(limit).all()
