"""Agents API routes."""
from fastapi import APIRouter
agents_router = APIRouter(prefix="/api/agents", tags=["agents"])
@agents_router.get("/health")
async def agents_health(): return {"module": "agents", "status": "active"}
