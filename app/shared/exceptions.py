"""
Shared exceptions for cross-module error handling.
"""


class AFAQException(Exception):
    """Base exception for all AFAQ-OS errors."""
    def __init__(self, message: str = "An AFAQ-OS error occurred"):
        self.message = message
        super().__init__(self.message)


class ModuleNotFound(AFAQException):
    def __init__(self, slug: str):
        super().__init__(f"Module '{slug}' not found in registry")


class ModuleDisabled(AFAQException):
    def __init__(self, slug: str):
        super().__init__(f"Module '{slug}' is disabled — feature flag is off")


class FeatureFlagDisabled(AFAQException):
    def __init__(self, flag: str):
        super().__init__(f"Feature flag '{flag}' is disabled")


class InvalidConfiguration(AFAQException):
    def __init__(self, key: str):
        super().__init__(f"Invalid or missing configuration key: '{key}'")