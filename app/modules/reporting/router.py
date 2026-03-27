"""Reporting API routes."""
from fastapi import APIRouter
reporting_router = APIRouter(prefix="/api/reporting", tags=["reporting"])
@reporting_router.get("/health")
async def reporting_health(): return {"module": "reporting", "status": "active"}
