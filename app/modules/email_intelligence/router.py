"""Email Intelligence API routes."""
from fastapi import APIRouter
email_intelligence_router = APIRouter(prefix="/api/email_intelligence", tags=["email_intelligence"])
@email_intelligence_router.get("/health")
async def email_intelligence_health(): return {"module": "email_intelligence", "status": "active"}
