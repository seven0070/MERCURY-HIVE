from sqlalchemy.orm import Session
from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventCreate

def log_event(db: Session, event_in: AuditEventCreate):
    """
    Append-only logging of an event.
    """
    db_event = AuditEvent(
        actor_id=event_in.actor_id,
        action=event_in.action,
        target_resource=event_in.target_resource,
        result=event_in.result,
        reason=event_in.reason,
        metadata_json=event_in.metadata_json
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_audit_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()
