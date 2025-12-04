"""Example demonstrating SecretsManager + Provider Registry usage.

This demo shows how to retrieve an API key via `SecretsManager` and
instantiate a registered provider from configuration.
"""
from api_engine.secrets_manager import SecretsManager
from api_engine.mail_service import MailService


def demo_send_email():
    # MailService will read provider config from configs via ConfigManager
    ms = MailService()
    try:
        result = ms.send_email(
            to="recipient@example.com",
            subject="Test from BI Platform",
            content="<p>This is a test email from BI Platform.</p>",
            # provider name optional; if not provided, MailService uses default from config
        )
        print("Email send result:", result)
    except Exception as e:
        print("Failed to send email:", e)


if __name__ == "__main__":
    demo_send_email()
