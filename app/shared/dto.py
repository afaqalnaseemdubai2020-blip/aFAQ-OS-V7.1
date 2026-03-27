"""
Shared DTOs (Data Transfer Objects) used across API boundaries.
"""

from pydantic import BaseModel
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int


class HealthCheckResponse(BaseModel):
    app: str
    version: str
    environment: str
    timezone: str
    modules: Dict[str, bool]


class ModuleInfoResponse(BaseModel):
    name: str
    slug: str
    version: str
    status: str
    description: str
    icon: Optional[str] = None
    category: str


class ModulesListResponse(BaseModel):
    total: int
    active: int
    coming_soon: int
    modules: List[ModuleInfoResponse]