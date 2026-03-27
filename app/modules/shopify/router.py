"""Shopify API routes."""
from fastapi import APIRouter
shopify_router = APIRouter(prefix="/api/shopify", tags=["shopify"])
@shopify_router.get("/health")
async def shopify_health(): return {"module": "shopify", "status": "active"}
