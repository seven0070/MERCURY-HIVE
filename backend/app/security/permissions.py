from app.models.agent import Agent
from sqlalchemy.orm import Session
from app.audit.service import log_event
from app.schemas.audit import AuditEventCreate
from fastapi import Depends, HTTPException, Header
from app.db.session import get_db

# Role hierarchy: lower index = higher authority
ROLE_HIERARCHY = {
    "Owner": 0,
    "CEO": 1,
    "HR": 2,
    "Department Manager": 3,
    "Worker": 4,
    "Temporary Sub-Agent": 5
}

def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role, 999)

def evaluate_permission(db: Session, actor: Agent, action: str, target: Agent = None, resource: str = None) -> bool:
    """
    Evaluates if the actor can perform the action on the target/resource.
    Enforces Owner supremacy, hierarchy rules, and deny-by-default.
    """
    result = "DENY"
    reason = "Default deny"
    is_allowed = False

    try:
        # 1. Owner Supremacy
        if actor.role == "Owner":
            is_allowed = True
            reason = "Owner has unrestricted authority"
            return is_allowed

        # Agents cannot modify the owner
        if target and target.role == "Owner":
            reason = "Cannot modify the Owner"
            return is_allowed

        # 2. Self-modification rules
        if target and actor.id == target.id:
            if action in ["modify_permissions", "grant_permissions", "assign_role", "change_status"]:
                reason = "Agent cannot elevate or modify own permissions/status"
                return is_allowed

        # 3. Hierarchy Rules
        if target:
            actor_level = get_role_level(actor.role)
            target_level = get_role_level(target.role)

            if action == "create_agent" and resource: # resource contains the role to create
                created_role_level = get_role_level(resource)
                if actor_level >= created_role_level:
                    reason = "Cannot create agent with equal or higher role"
                    return is_allowed

            if action in ["change_status", "assign_role", "modify_agent"]:
                if actor_level >= target_level:
                    reason = "Cannot modify agent with equal or higher role"
                    return is_allowed

        # 4. Specific Action rules
        if action == "read_agent":
            # For now, anyone can read agents. Can tighten later.
            is_allowed = True
            reason = "Read access granted"

        if action == "read_audit":
            if actor.role not in ["CEO", "HR"]:
                reason = "Only CEO/HR/Owner can read audit logs"
                return is_allowed
            is_allowed = True
            reason = "Audit read access granted"

        if action == "execute_task":
            if actor.role in ["Worker", "Temporary Sub-Agent", "Department Manager", "CEO"]:
                is_allowed = True
                reason = "Agent is authorized to execute tasks"
                return is_allowed

        if action == "send_message":
            if target:
                if actor.department == target.department:
                    is_allowed = True
                    reason = "Same department message allowed"
                    return is_allowed
                else:
                    reason = "Cross department message denied without bridge"
                    return is_allowed

        # Explicitly define allow cases here. If not matched, it defaults to deny.

        if action == "use_model_gateway":
            if actor.role in ["Owner", "CEO"]:
                is_allowed = True
                reason = "Owner/CEO can directly access gateway"
                return is_allowed

    finally:
        result = "ALLOW" if is_allowed else "DENY"
        # Log the permission check
        log_event(
            db=db,
            event_in=AuditEventCreate(
                actor_id=actor.id if actor else "UNKNOWN",
                action=action,
                target_resource=target.id if target else resource,
                result=result,
                reason=reason
            )
        )

    return is_allowed

def require_permission(action: str):
    def dependency(x_actor_id: str = Header(...), db: Session = Depends(get_db)) -> Agent:
        actor = db.query(Agent).filter(Agent.id == x_actor_id).first()
        if not actor:
            raise HTTPException(status_code=401, detail="Actor not found")
        if not evaluate_permission(db, actor, action):
            raise HTTPException(status_code=403, detail=f"Permission denied for action: {action}")
        return actor
    return dependency
