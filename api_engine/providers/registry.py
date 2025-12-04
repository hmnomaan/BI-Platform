"""Simple provider registry for API Engine.

Allows adapters to be registered and retrieved by logical name. This enables
switching providers via configuration without changing call sites.
"""
from typing import Dict, Type, Any


class ProviderRegistry:
    def __init__(self):
        self._registry: Dict[str, Type[Any]] = {}

    def register(self, name: str, provider_cls: Type[Any]):
        """Register a provider class under a logical name."""
        self._registry[name.lower()] = provider_cls

    def get(self, name: str):
        """Get a provider class by name (case-insensitive)."""
        return self._registry.get(name.lower())

    def list_providers(self):
        return list(self._registry.keys())


default_registry = ProviderRegistry()


def register_provider(name: str, provider_cls: Type[Any]):
    default_registry.register(name, provider_cls)


def get_provider(name: str):
    return default_registry.get(name)


__all__ = ["ProviderRegistry", "default_registry", "register_provider", "get_provider"]
