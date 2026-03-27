
"""
Inventory Module — Stock tracking, reorder alerts, warehouse ops.
"""

from fastapi import APIRouter
from app.core.domain.module import ModuleInfo, ModuleStatus, ModuleContract
from app.core.module_registry import module_registry
from app.core.feature_flags import feature_flags
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="Inventory",
    version="1.0.0",
    slug="inventory",
    description="Stock tracking, reorder alerts, warehouse ops",
    feature_flag_key="inventory",
    icon="📦",
    category="operations",
    api_prefix="/api/inventory",
    created_at=datetime(2025, 3, 27),
)


class Module(ModuleContract):
    def get_info(self) -> ModuleInfo:
        return MODULE_INFO

    def register_routes(self, router) -> None:
        from .router import inventory_router
        router.include_router(inventory_router)

    def register_events(self, event_bus) -> None:
        pass

    async def health_check(self) -> bool:
        return True

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    def get_api_prefix(self) -> str:
        return MODULE_INFO.api_prefix


module_registry.register("inventory", MODULE_INFO, Module())
