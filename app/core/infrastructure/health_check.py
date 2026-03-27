"""
Health check service — combines app metadata with module health.
"""

from app.core.config import settings
from app.core.module_registry import module_registry
from app.shared.dto import HealthCheckResponse


async def get_health_status() -> HealthCheckResponse:
    module_health = await module_registry.health_check_all()
    return HealthCheckResponse(
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timezone=settings.TIMEZONE,
        modules=module_health,
    )
