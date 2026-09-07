import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.models.agent import Agent
from app.models.department import Department
from app.models.task import Task
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
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    initialize_owner(db_session)
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_task_result_submission(db):
    owner = db.query(Agent).filter(Agent.role == "Owner").first()

    # Create dept
    dept = Department(name="Engineering")
    db.add(dept)
    db.commit()
    db.refresh(dept)

    # Create worker
    worker = Agent(display_name="Test Worker", role="Worker", department=dept.id)
    db.add(worker)
    db.commit()
    db.refresh(worker)

    # Create task
    task = Task(title="Test Task", description="Test Desc", creator_id=owner.id, assigned_to_id=worker.id, department_id=dept.id)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Non-assignee trying to submit result should fail
    response = client.post(
        f"/tasks/{task.id}/results",
        json={"status": "Success", "output_data": "Done"},
        headers={"X-Actor-ID": owner.id}
    )
    assert response.status_code == 403
    assert "Only assigned agent can submit result" in response.json()["detail"]

    # Assignee trying to submit result should succeed
    response = client.post(
        f"/tasks/{task.id}/results",
        json={"status": "Success", "output_data": "Done"},
        headers={"X-Actor-ID": worker.id}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Success"

def test_message_department_isolation(db):
    dept1 = Department(name="HR")
    dept2 = Department(name="IT")
    db.add_all([dept1, dept2])
    db.commit()

    worker1 = Agent(display_name="W1", role="Worker", department=dept1.id)
    worker2 = Agent(display_name="W2", role="Worker", department=dept2.id)
    db.add_all([worker1, worker2])
    db.commit()

    # Worker in HR cannot send to IT without bridge
    response = client.post(
        "/messages/",
        json={"receiver_id": worker2.id, "content": "Hello IT"},
        headers={"X-Actor-ID": worker1.id}
    )
    assert response.status_code == 403
