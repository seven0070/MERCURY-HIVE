import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate
from app.services import agent_service
from fastapi import HTTPException

client = TestClient(app)

def test_invalid_status_transitions_rejected(db):
    owner = Agent(role="Owner", display_name="Owner", status="Active")
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(owner)
    db.add(worker)
    db.commit()

    with pytest.raises(HTTPException) as excinfo:
        agent_service.change_status(db, worker.id, "InvalidStatus", owner)
    assert excinfo.value.status_code == 400
    assert "Invalid status" in excinfo.value.detail

def test_terminated_agents_remain_in_records(db):
    owner = Agent(role="Owner", display_name="Owner", status="Active")
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(owner)
    db.add(worker)
    db.commit()

    agent_service.change_status(db, worker.id, "Terminated", owner)

    terminated_agent = agent_service.get_agent(db, worker.id)
    assert terminated_agent is not None
    assert terminated_agent.status == "Terminated"

def test_hierarchy_enforcement(db):
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    ceo = Agent(role="CEO", display_name="CEO", status="Active")
    db.add(worker)
    db.add(ceo)
    db.commit()

    # Worker cannot modify CEO status
    with pytest.raises(HTTPException) as excinfo:
        agent_service.change_status(db, ceo.id, "Suspended", worker)
    assert excinfo.value.status_code == 403

def test_hierarchy_creation_restrictions(db):
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(worker)
    db.commit()

    with pytest.raises(HTTPException) as excinfo:
        agent_service.register_agent(db, AgentCreate(display_name="CEO2", role="CEO"), worker)
    assert excinfo.value.status_code == 403
