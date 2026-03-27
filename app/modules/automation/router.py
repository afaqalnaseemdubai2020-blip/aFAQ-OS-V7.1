"""Automation API routes."""
from fastapi import APIRouter
automation_router = APIRouter(prefix="/api/automation", tags=["automation"])
@automation_router.get("/health")
async def automation_health(): return {"module": "automation", "status": "active"}
