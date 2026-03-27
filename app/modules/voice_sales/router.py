"""Voice Sales API routes."""
from fastapi import APIRouter
voice_sales_router = APIRouter(prefix="/api/voice_sales", tags=["voice_sales"])
@voice_sales_router.get("/health")
async def voice_sales_health(): return {"module": "voice_sales", "status": "active"}
