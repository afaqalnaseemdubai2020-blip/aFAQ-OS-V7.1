"""
Feature flag manager — controls module visibility and lock state.
All flags start FALSE. Modules unlocked one by one via .env edits.
"""

import json
import logging
from typing import Dict, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class FeatureFlagManager:
    def __init__(self):
        self._flags: Dict[str, bool] = settings.feature_flags_dict
        logger.info(f"Feature flags loaded: {len(self._flags)} flags, "
                     f"{sum(1 for v in self._flags.values() if v)} enabled")

    def is_enabled(self, module_slug: str) -> bool:
        return self._flags.get(module_slug, False)

    def get_all(self) -> Dict[str, bool]:
        return dict(self._flags)

    def enable(self, module_slug: str) -> None:
        self._flags[module_slug] = True
        logger.info(f"Feature flag ENABLED: {module_slug}")

    def disable(self, module_slug: str) -> None:
        self._flags[module_slug] = False
        logger.info(f"Feature flag DISABLED: {module_slug}")

    @property
    def enabled_modules(self) -> List[str]:
        return [k for k, v in self._flags.items() if v]

    @property
    def disabled_modules(self) -> List[str]:
        return [k for k, v in self._flags.items() if not v]


feature_flags = FeatureFlagManager()
