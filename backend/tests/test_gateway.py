import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.models.agent import Agent
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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    initialize_owner(db_session)
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_gateway_access_owner(db):
    owner = db.query(Agent).filter(Agent.role == "Owner").first()

    response = client.post(
        "/gateway/generate",
        json={"system_prompt": "You are helpful.", "messages": [{"content": "Say hello"}]},
        headers={"X-Actor-ID": owner.id}
    )
    assert response.status_code == 200
    assert "SIMULATED LLM RESPONSE" in response.json()["content"]

def test_gateway_access_worker_denied(db):
    worker = Agent(display_name="Test Worker", role="Worker")
    db.add(worker)
    db.commit()
    db.refresh(worker)

    response = client.post(
        "/gateway/generate",
        json={"system_prompt": "You are helpful.", "messages": [{"content": "Say hello"}]},
        headers={"X-Actor-ID": worker.id}
    )
    assert response.status_code == 403

def test_runtime_execution(db):
    worker = Agent(display_name="Test Worker", role="Worker")
    db.add(worker)
    db.commit()
    db.refresh(worker)

    from app.services.agent_runtime import get_runtime
    runtime = get_runtime(db, worker)
    # Workers are allowed to call execute_agent_step inside their runtime sandbox
    resp = runtime.execute_agent_step("System", [{"content": "msg"}])
    assert "SIMULATED LLM RESPONSE" in resp
