from app.models.agent import Agent
from app.security.permissions import evaluate_permission

def test_owner_highest_authority(db):
    owner = Agent(role="Owner", display_name="Owner", status="Active")
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(owner)
    db.add(worker)
    db.commit()

    # Owner can create a worker
    assert evaluate_permission(db, owner, "create_agent", resource="Worker") is True
    # Owner can terminate worker
    assert evaluate_permission(db, owner, "change_status", target=worker) is True

def test_worker_cannot_create_ceo(db):
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(worker)
    db.commit()

    assert evaluate_permission(db, worker, "create_agent", resource="CEO") is False

def test_worker_cannot_modify_own_permissions(db):
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(worker)
    db.commit()

    assert evaluate_permission(db, worker, "modify_permissions", target=worker) is False
    assert evaluate_permission(db, worker, "grant_permissions", target=worker) is False
    assert evaluate_permission(db, worker, "change_status", target=worker) is False

def test_unknown_permissions_default_deny(db):
    worker = Agent(role="Worker", display_name="Worker", status="Active")
    db.add(worker)
    db.commit()

    assert evaluate_permission(db, worker, "make_coffee") is False
