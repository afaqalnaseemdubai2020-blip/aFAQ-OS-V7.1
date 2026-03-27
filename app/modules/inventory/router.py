
"""
Inventory API routes.
"""

from fastapi import APIRouter
from app.shared.dto import HealthCheckResponse

inventory_router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@inventory_router.get("/health")
async def inventory_health():
    return {"module": "inventory", "status": "active"}
