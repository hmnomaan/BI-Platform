"""
BI Platform API Engine

A modular API engine for integrating with various third-party services.
"""

from .core.api_engine import APIEngine
from .core.config_manager import ConfigManager
from .core.abstract_providers import (
    EmailProvider,
    StorageProvider,
    SigningProvider,
    SearchProvider,
    PhysicalMailProvider
)

__version__ = "0.1.0"
__all__ = [
    "APIEngine",
    "ConfigManager",
    "EmailProvider",
    "StorageProvider",
    "SigningProvider",
    "SearchProvider",
    "PhysicalMailProvider",
]

