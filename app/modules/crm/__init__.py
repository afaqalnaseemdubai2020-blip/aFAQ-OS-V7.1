"""
CRM Module — lead management, conversion tracking.
"""
from fastapi import APIRouter
from app.core.domain.module import ModuleInfo, ModuleContract
from app.core.module_registry import module_registry
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="CRM", version="1.0.0", slug="crm",
    description="Lead management, pipeline tracking, conversion analytics",
    feature_flag_key="crm", icon="📊", category="sales",
    api_prefix="/api/crm", created_at=datetime(2025, 3, 27),
)

class Module(ModuleContract):
    def get_info(self): return MODULE_INFO
    def register_routes(self, router): pass
    def register_events(self, event_bus): pass
    async def health_check(self): return True
    async def on_startup(self): pass
    async def on_shutdown(self): pass
    def get_api_prefix(self): return MODULE_INFO.api_prefix

module_registry.register("crm", MODULE_INFO, Module())
