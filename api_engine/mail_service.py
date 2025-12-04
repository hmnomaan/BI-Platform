"""Standardized mail service wrapper.

This module provides `MailService` which initializes an email provider
using the provider registry and retrieves API keys via `SecretsManager`.
It exposes a unified `send_email` method.
"""
from typing import Dict, Any, Optional
import os
from api_engine.providers.registry import get_provider
from api_engine.secrets_manager import SecretsManager
from api_engine.core.config_manager import ConfigManager
from api_engine.utils.logging import get_logger


logger = get_logger("MailService")


class MailService:
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_manager: Optional[ConfigManager] = None):
        """Create MailService.

        Args:
            config: optional dict with provider defaults (overrides config_manager)
            config_manager: optional ConfigManager to read `api_config.yaml`
        """
        self.config_manager = config_manager or ConfigManager()
        # top-level mail config can be passed or read from config manager
        # Also allow environment variable override for default provider name:
        #   API_PROVIDERS_EMAIL_PROVIDER=dummy
        self.config = config or self.config_manager.get("providers.email") or {}
        env_provider = os.getenv("API_PROVIDERS_EMAIL_PROVIDER") or os.getenv("EMAIL_PROVIDER")
        if env_provider:
            # ensure the provider selection is present in the runtime config
            self.config.setdefault("provider", env_provider)
        self.secrets = SecretsManager()

    def _init_provider(self, provider_name: str, provider_cfg: Dict[str, Any]):
        provider_cls = get_provider(provider_name)
        if provider_cls is None:
            raise ValueError(f"Email provider '{provider_name}' is not registered")

        # If config references a secret path for the api_key, retrieve it
        api_key = provider_cfg.get("api_key")
        secret_path = provider_cfg.get("api_key_secret_path")
        if not api_key and secret_path:
            api_key = self.secrets.get_secret(secret_path)

        init_cfg = dict(provider_cfg)
        if api_key:
            init_cfg["api_key"] = api_key

        # Remove secret path before initializing
        init_cfg.pop("api_key_secret_path", None)

        provider = provider_cls(init_cfg)
        return provider

    def send_email(self, to: str, subject: str, content: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Send email using selected provider.

        provider: logical name (e.g., 'sendgrid' or 'mailgun'). If None, uses default from config.
        Additional args (cc, bcc, attachments) are passed through.
        """
        provider_name = provider or self.config.get("provider") or "sendgrid"
        provider_cfg = self.config_manager.get(f"providers.email.{provider_name}", {})
        # Merge with any overrides provided in self.config
        merged_cfg = {**provider_cfg, **(self.config or {})}

        mail_provider = self._init_provider(provider_name, merged_cfg)

        try:
            result = mail_provider.send_email(to=to, subject=subject, content=content, **kwargs)
            logger.info(f"Email sent via {provider_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to send email via {provider_name}: {e}")
            # For now re-raise so callers can handle retry/failover
            raise


__all__ = ["MailService"]
