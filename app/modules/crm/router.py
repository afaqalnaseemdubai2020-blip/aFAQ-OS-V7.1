"""CRM API routes."""
from fastapi import APIRouter
crm_router = APIRouter(prefix="/api/crm", tags=["crm"])
@crm_router.get("/health")
async def crm_health(): return {"module": "crm", "status": "active"}
