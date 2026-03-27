"""Employee Module — attendance, check-in, productivity."""
from app.core.domain.module import ModuleInfo, ModuleContract
from app.core.module_registry import module_registry
from datetime import datetime

MODULE_INFO = ModuleInfo(
    name="Employee", version="1.0.0", slug="employee",
    description="Attendance, check-in, overtime, productivity",
    feature_flag_key="employee", icon="👥", category="management",
    api_prefix="/api/employee", created_at=datetime(2025, 3, 27),
)

class Module(ModuleContract):
    def get_info(self): return MODULE_INFO
    def register_routes(self, router): pass
    def register_events(self, event_bus): pass
    async def health_check(self): return True
    async def on_startup(self): pass
    async def on_shutdown(self): pass
    def get_api_prefix(self): return MODULE_INFO.api_prefix

module_registry.register("employee", MODULE_INFO, Module())
