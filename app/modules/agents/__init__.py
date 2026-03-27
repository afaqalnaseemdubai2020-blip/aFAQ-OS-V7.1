"""Agents Module — cron-driven agents, background jobs."""
from app.core.domain.module import ModuleInfo, ModuleContract
from app.core.module_registry import module_registry
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="Agents", version="1.0.0", slug="agents",
    description="Cron-driven agents, background jobs, scheduled tasks",
    feature_flag_key="agents", icon="🤖", category="automation",
    api_prefix="/api/agents", created_at=datetime(2025, 3, 27),
)

class Module(ModuleContract):
    def get_info(self): return MODULE_INFO
    def register_routes(self, router): pass
    def register_events(self, event_bus): pass
    async def health_check(self): return True
    async def on_startup(self): pass
    async def on_shutdown(self): pass
    def get_api_prefix(self): return MODULE_INFO.api_prefix

module_registry.register("agents", MODULE_INFO, Module())
