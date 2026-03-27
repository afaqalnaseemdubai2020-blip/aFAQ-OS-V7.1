"""
Core module abstraction — every module must conform to this contract.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Protocol
from datetime import datetime


class ModuleStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    COMING_SOON = "coming_soon"
    ERROR = "error"
    LOADING = "loading"


@dataclass(frozen=True)
class ModuleInfo:
    name: str
    version: str
    slug: str
    description: str
    status: ModuleStatus = ModuleStatus.DISABLED
    feature_flag_key: Optional[str] = None
    icon: Optional[str] = None
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    api_prefix: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ModuleContract(Protocol):
    def get_info(self) -> ModuleInfo: ...
    def register_routes(self, router) -> None: ...
    def register_events(self, event_bus) -> None: ...
    async def health_check(self) -> bool: ...
    async def on_startup(self) -> None: ...
    async def on_shutdown(self) -> None: ...
    def get_api_prefix(self) -> str: ...