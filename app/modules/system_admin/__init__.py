"""System Admin Module — user management, audit logs, config."""
from app.core.domain.module import ModuleInfo, ModuleContract
from app.core.module_registry import module_registry
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="System Admin", version="1.0.0", slug="system_admin",
    description="User management, audit logs, config hot-reload",
    feature_flag_key="system_admin", icon="🔐", category="infrastructure",
    api_prefix="/api/system_admin", created_at=datetime(2025, 3, 27),
)

class Module(ModuleContract):
    def get_info(self): return MODULE_INFO
    def register_routes(self, router): pass
    def register_events(self, event_bus): pass
    async def health_check(self): return True
    async def on_startup(self): pass
    async def on_shutdown(self): pass
    def get_api_prefix(self): return MODULE_INFO.api_prefix

module_registry.register("system_admin", MODULE_INFO, Module())
