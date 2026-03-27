"""Scheduling API routes."""
from fastapi import APIRouter
scheduling_router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])
@scheduling_router.get("/health")
async def scheduling_health(): return {"module": "scheduling", "status": "active"}
