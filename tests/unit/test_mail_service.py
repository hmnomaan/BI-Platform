import os
from api_engine.mail_service import MailService
from api_engine.providers.registry import register_provider


class DummyEmailProvider:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}

    def send_email(self, to, subject, content, **kwargs):
        return {"status": "success", "to": to, "subject": subject}


def test_mail_service_with_env(monkeypatch):
    # register dummy provider
    register_provider("dummy", DummyEmailProvider)
    # set default provider in config via env as fallback
    monkeypatch.setenv("API_PROVIDERS_EMAIL_PROVIDER", "dummy")
    ms = MailService()
    res = ms.send_email("a@b.com", "hi", "hello")
    assert res["status"] == "success"
