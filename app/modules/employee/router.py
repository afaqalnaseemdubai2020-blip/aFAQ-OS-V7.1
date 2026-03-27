"""Employee API routes."""
from fastapi import APIRouter
employee_router = APIRouter(prefix="/api/employee", tags=["employee"])
@employee_router.get("/health")
async def employee_health(): return {"module": "employee", "status": "active"}
