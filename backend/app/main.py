from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import health, agents, audit, permissions
from app.db.session import SessionLocal
from app.services.agent_service import initialize_owner

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize owner on startup
    db = SessionLocal()
    try:
        initialize_owner(db)
    finally:
        db.close()
    yield

app = FastAPI(title="Mercury Hive Control Plane API", lifespan=lifespan)

app.include_router(health.router)
app.include_router(agents.router)
app.include_router(audit.router)
app.include_router(permissions.router)
