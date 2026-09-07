# Mercury Hive - Backend (Control Plane)

The backend provides the authoritative Control Plane for the Mercury Hive system. It enforces ownership, identity, roles, permissions, agent lifecycle, and audit logging.

## Build 1 Implementation Details:
- **Framework:** FastAPI
- **Database:** PostgreSQL (using SQLite for dev currently) + SQLAlchemy + Alembic
- **Core Models:** `Agent`, `AuditEvent`
- **Security:** Evaluates permissions based on Owner supremacy and default-deny policies.
- **Audit:** Append-only event logging for tracking access requests and state changes.

## Out of Scope for Build 1
- LLM calls or model integrations
- Reasoning logic for CEO, HR, or other agents
- Autonomous agent behavior
- Full-fledged authentication providers
