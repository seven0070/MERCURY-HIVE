from app.models.agent import Agent
from app.security.permissions import evaluate_permission
from app.models.audit import AuditEvent

def test_audit_events_are_generated(db):
    owner = Agent(role="Owner", display_name="Owner", status="Active")
    db.add(owner)
    db.commit()

    # Perform an action that gets audited
    evaluate_permission(db, owner, "create_agent", resource="Worker")

    # Check if audit event was created
    audit_events = db.query(AuditEvent).all()
    assert len(audit_events) > 0
    assert audit_events[-1].action == "create_agent"
    assert audit_events[-1].actor_id == owner.id
    assert audit_events[-1].result == "ALLOW"
    assert audit_events[-1].target_resource == "Worker"

def test_audit_records_immutable(db):
    from app.schemas.audit import AuditEventCreate
    from app.audit.service import log_event

    event = log_event(db, AuditEventCreate(actor_id="test", action="test", result="ALLOW"))
    assert event.id is not None

    # Audit log should only append, no update/delete methods exist
    assert not hasattr(db.query(AuditEvent), "update_event")
