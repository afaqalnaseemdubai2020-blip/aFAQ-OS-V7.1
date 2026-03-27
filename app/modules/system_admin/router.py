"""System Admin API routes."""
from fastapi import APIRouter
system_admin_router = APIRouter(prefix="/api/system_admin", tags=["system_admin"])
@system_admin_router.get("/health")
async def system_admin_health(): return {"module": "system_admin", "status": "active"}
