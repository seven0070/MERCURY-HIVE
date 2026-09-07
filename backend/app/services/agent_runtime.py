from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.models.task import Task, TaskResult
from app.models.message import AgentMessage
from app.schemas.task import TaskCreate, TaskUpdate, TaskResultCreate
from app.schemas.message import AgentMessageCreate
from app.security.permissions import evaluate_permission
from app.services.model_gateway import gateway
from app.services.agent_service import get_agent
from fastapi import HTTPException
from datetime import datetime

class AgentRuntime:
    def __init__(self, db: Session, actor: Agent):
        self.db = db
        self.actor = actor

    def create_task(self, task_in: TaskCreate) -> Task:
        target = get_agent(self.db, task_in.assigned_to_id) if task_in.assigned_to_id else None
        if not evaluate_permission(self.db, self.actor, "assign_task", target=target):
            raise HTTPException(status_code=403, detail="Permission denied to assign task")
        task = Task(**task_in.model_dump(), creator_id=self.actor.id)
        if not task.department_id:
            task.department_id = getattr(self.actor, 'department_id', None)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_status(self, task_id: str, status: str) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.assigned_to_id != self.actor.id and task.creator_id != self.actor.id and self.actor.role not in ["CEO", "HR"]:
            raise HTTPException(status_code=403, detail="Only assignee, creator, or admin can update task")
        task.status = status
        if status == "InProgress" and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in ["Completed", "Failed", "Canceled"]:
            task.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def submit_task_result(self, task_id: str, result_in: TaskResultCreate) -> TaskResult:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.assigned_to_id != self.actor.id:
            raise HTTPException(status_code=403, detail="Only assigned agent can submit result")
        if not evaluate_permission(self.db, self.actor, "execute_task", target=self.actor):
             raise HTTPException(status_code=403, detail="Permission denied to execute task")
        result = TaskResult(**result_in.model_dump(), task_id=task.id, agent_id=self.actor.id)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        if result.status == "Success":
            self.update_task_status(task.id, "Completed")
        return result

    def send_message(self, message_in: AgentMessageCreate) -> AgentMessage:
        target = get_agent(self.db, message_in.receiver_id) if message_in.receiver_id else None
        if not evaluate_permission(self.db, self.actor, "send_message", target=target):
            raise HTTPException(status_code=403, detail="Permission denied to send message to target")
        msg = AgentMessage(**message_in.model_dump(), sender_id=self.actor.id)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def execute_agent_step(self, system_prompt: str, messages: list) -> str:
        if not evaluate_permission(self.db, self.actor, "execute_task", target=self.actor):
            raise HTTPException(status_code=403, detail="Permission denied to execute")
        from app.schemas.gateway import GatewayRequest
        request = GatewayRequest(system_prompt=system_prompt, messages=messages)
        response = gateway.generate_response(request).content
        return response

def get_runtime(db: Session, actor: Agent) -> AgentRuntime:
    return AgentRuntime(db, actor)
