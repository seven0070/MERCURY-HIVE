import logging
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResultCreate
from app.services.agent_runtime import get_runtime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TaskOrchestrator:
    def __init__(self, db: Session, owner_actor: Agent):
        self.db = db
        # Orchestrator usually runs as Owner/CEO
        self.actor = owner_actor
        if self.actor.role not in ["Owner", "CEO"]:
            raise HTTPException(status_code=403, detail="Only Owner/CEO can orchestrate")

    def orchestrate_task(self, title: str, description: str, target_department_id: str = None) -> str:
        """
        Orchestrates an end-to-end task cycle.
        """
        runtime = get_runtime(self.db, self.actor)

        # 1. Task Planning
        # Find best agent
        from app.models.agent import Agent
        from app.models.department import Department

        assigned_agent = None
        if target_department_id:
            assigned_agent = self.db.query(Agent).filter(
                Agent.department == target_department_id,
                Agent.role == "Worker",
                Agent.status == "Active"
            ).first()

        if not assigned_agent:
            # Fallback to any active worker
            assigned_agent = self.db.query(Agent).filter(Agent.role == "Worker", Agent.status == "Active").first()

        if not assigned_agent:
            # If no worker exists, we simulate an escalation.
            return "ESCALATION: No eligible workers available to execute the task."

        # 2. Agent Assignment & Task Creation
        task_in = TaskCreate(
            title=title,
            description=description,
            department_id=assigned_agent.department,
            assigned_to_id=assigned_agent.id
        )
        task = runtime.create_task(task_in)

        # 3. Agent Runtime Execution
        worker_runtime = get_runtime(self.db, assigned_agent)
        worker_runtime.update_task_status(task.id, "InProgress")

        system_prompt = f"You are a Mercury Hive Worker Agent. Execute this task: {task.title}"
        messages = [{"role": "user", "content": task.description}]

        # 4. Model Gateway & AI Model
        try:
            model_response = worker_runtime.execute_agent_step(system_prompt=system_prompt, messages=messages)

            # 5. Task Result Submission
            result_in = TaskResultCreate(status="Success", output_data=model_response)
            worker_runtime.submit_task_result(task.id, result_in)

            return f"Task completed successfully by {assigned_agent.display_name}. Output: {model_response}"
        except Exception as e:
            # Result / Escalation
            result_in = TaskResultCreate(status="Failed", error_details=str(e))
            worker_runtime.submit_task_result(task.id, result_in)
            return f"ESCALATION: Task failed. Details: {str(e)}"
