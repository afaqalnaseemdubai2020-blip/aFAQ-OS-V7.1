"""
Auto-discovery module loader — imports all module packages under app/modules/.
Each module self-registers with module_registry on import.
"""

import importlib
import logging
import pkgutil

logger = logging.getLogger(__name__)


def discover_modules() -> None:
    """Import each module package so self-registration fires."""
    from app.modules import __path__ as modules_path

    for importer, modname, ispkg in pkgutil.iter_modules(modules_path):
        if ispkg:
            try:
                full_name = f"app.modules.{modname}"
                importlib.import_module(full_name)
                logger.info(f"Discovered module: {modname}")
            except Exception as e:
                logger.error(f"Failed to load module [{modname}]: {e}")
