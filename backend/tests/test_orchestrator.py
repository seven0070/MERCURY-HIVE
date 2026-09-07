import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.models.agent import Agent
from app.models.department import Department
from app.models.task import Task, TaskResult
from app.services.agent_service import initialize_owner

# Set up test database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

from app.db.session import get_db
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    initialize_owner(db_session)
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_full_task_orchestration(db):
    owner = db.query(Agent).filter(Agent.role == "Owner").first()

    # 1. Create a Department & Worker
    dept = Department(name="Research")
    db.add(dept)
    db.commit()
    db.refresh(dept)

    worker = Agent(display_name="Researcher Alpha", role="Worker", department=dept.id, status="Active")
    db.add(worker)
    db.commit()

    # 2. Owner triggers Orchestration
    req_payload = {
        "title": "Analyze Data",
        "description": "Please analyze the datasets.",
        "department_id": dept.id
    }

    resp = client.post(
        "/orchestration/execute",
        json=req_payload,
        headers={"X-Actor-ID": owner.id}
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "Success"
    assert "Task completed successfully" in resp.json()["detail"]
    assert "SIMULATED LLM RESPONSE" in resp.json()["detail"]

    # 3. Verify Database State
    task = db.query(Task).filter(Task.title == "Analyze Data").first()
    assert task is not None
    assert task.status == "Completed"
    assert task.assigned_to_id == worker.id

    task_result = db.query(TaskResult).filter(TaskResult.task_id == task.id).first()
    assert task_result is not None
    assert task_result.status == "Success"
    assert "SIMULATED LLM RESPONSE" in task_result.output_data

def test_orchestration_escalation(db):
    owner = db.query(Agent).filter(Agent.role == "Owner").first()
    # Intentionally do not create any active workers

    req_payload = {
        "title": "Impossible Task",
        "description": "Do something."
    }

    resp = client.post(
        "/orchestration/execute",
        json=req_payload,
        headers={"X-Actor-ID": owner.id}
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "Failed"
    assert "ESCALATION: No eligible workers" in resp.json()["detail"]
