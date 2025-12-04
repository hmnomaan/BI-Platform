import os
from api_engine.secrets_manager import SecretsManager
from api_engine.providers.registry import register_provider, get_provider


def test_secrets_manager_env(monkeypatch):
    monkeypatch.setenv("TEST_SECRET_KEY", "abc123")
    sm = SecretsManager()
    assert sm.get_secret("test_secret_key") == "abc123"


def test_registry_register_and_get():
    class Dummy:
        def __init__(self, cfg=None):
            self.cfg = cfg

    register_provider("dummy", Dummy)
    cls = get_provider("dummy")
    assert cls is Dummy
