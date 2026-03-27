"""Content Automation API routes."""
from fastapi import APIRouter
content_automation_router = APIRouter(prefix="/api/content_automation", tags=["content_automation"])
@content_automation_router.get("/health")
async def content_automation_health(): return {"module": "content_automation", "status": "active"}
