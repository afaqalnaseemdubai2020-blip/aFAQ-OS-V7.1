"""
Central module registry — discovers, loads, and manages all modules.
"""

import logging
from typing import Dict, List, Optional
from app.core.domain.module import ModuleInfo, ModuleStatus
from app.core.feature_flags import feature_flags

logger = logging.getLogger(__name__)


class ModuleRegistry:
    def __init__(self):
        self._modules: Dict[str, dict] = {}

    def register(self, slug: str, info: ModuleInfo, instance=None) -> None:
        if feature_flags.is_enabled(slug):
            status = ModuleStatus.ACTIVE
        else:
            status = ModuleStatus.COMING_SOON

        updated_info = ModuleInfo(
            name=info.name,
            version=info.version,
            slug=info.slug,
            description=info.description,
            status=status,
            feature_flag_key=info.feature_flag_key,
            icon=info.icon,
            category=info.category,
            dependencies=info.dependencies,
            api_prefix=info.api_prefix,
            created_at=info.created_at,
        )

        self._modules[slug] = {"info": updated_info, "instance": instance}
        logger.info(f"Registered module [{slug}] v{info.version} → {status.value}")

    def get_module(self, slug: str) -> Optional[dict]:
        return self._modules.get(slug)

    def get_all_modules(self) -> List[ModuleInfo]:
        return [m["info"] for m in self._modules.values()]

    def get_active_modules(self) -> List[ModuleInfo]:
        return [
            m["info"]
            for m in self._modules.values()
            if m["info"].status == ModuleStatus.ACTIVE
        ]

    def get_coming_soon_modules(self) -> List[ModuleInfo]:
        return [
            m["info"]
            for m in self._modules.values()
            if m["info"].status == ModuleStatus.COMING_SOON
        ]

    async def health_check_all(self) -> Dict[str, bool]:
        results = {}
        for slug, data in self._modules.items():
            instance = data.get("instance")
            if instance and hasattr(instance, "health_check"):
                try:
                    results[slug] = await instance.health_check()
                except Exception:
                    results[slug] = False
            else:
                results[slug] = data["info"].status == ModuleStatus.ACTIVE
        return results

    async def startup_all(self) -> None:
        for slug, data in self._modules.items():
            instance = data.get("instance")
            if instance and data["info"].status == ModuleStatus.ACTIVE:
                if hasattr(instance, "on_startup"):
                    await instance.on_startup()
                    logger.info(f"Module [{slug}] started.")

    async def shutdown_all(self) -> None:
        for slug, data in self._modules.items():
            instance = data.get("instance")
            if instance and data["info"].status == ModuleStatus.ACTIVE:
                if hasattr(instance, "on_shutdown"):
                    await instance.on_shutdown()
                    logger.info(f"Module [{slug}] stopped.")


module_registry = ModuleRegistry()
