"""Shopify Module — product sync, order import, inventory bridge."""
from app.core.domain.module import ModuleInfo, ModuleContract
from app.core.module_registry import module_registry
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="Shopify", version="1.0.0", slug="shopify",
    description="Product sync, order import, inventory bridge",
    feature_flag_key="shopify", icon="🛒", category="integration",
    api_prefix="/api/shopify", created_at=datetime(2025, 3, 27),
)

class Module(ModuleContract):
    def get_info(self): return MODULE_INFO
    def register_routes(self, router): pass
    def register_events(self, event_bus): pass
    async def health_check(self): return True
    async def on_startup(self): pass
    async def on_shutdown(self): pass
    def get_api_prefix(self): return MODULE_INFO.api_prefix

module_registry.register("shopify", MODULE_INFO, Module())
