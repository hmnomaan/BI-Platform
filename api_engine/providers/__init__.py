"""Providers package initializer.

This module registers available provider classes with the provider registry so
they can be looked up by logical names in configuration.
"""
from . import email_providers
from .registry import register_provider

# Register known email providers
try:
    register_provider("sendgrid", email_providers.SendGridProvider)
except Exception:
    # registration should not break import if provider class not present
    pass

try:
    register_provider("mailgun", email_providers.MailgunProvider)
except Exception:
    pass

__all__ = ["email_providers", "register_provider"]
