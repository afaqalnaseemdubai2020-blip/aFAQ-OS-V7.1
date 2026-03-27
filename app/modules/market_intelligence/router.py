"""Market Intelligence API routes."""
from fastapi import APIRouter
market_intelligence_router = APIRouter(prefix="/api/market_intelligence", tags=["market_intelligence"])
@market_intelligence_router.get("/health")
async def market_intelligence_health(): return {"module": "market_intelligence", "status": "active"}
