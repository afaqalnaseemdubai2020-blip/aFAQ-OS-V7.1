
"""
Pricing API routes.
"""

from fastapi import APIRouter
from app.shared.dto import HealthCheckResponse

pricing_router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@pricing_router.get("/health")
async def pricing_health():
    return {"module": "pricing", "status": "active"}
