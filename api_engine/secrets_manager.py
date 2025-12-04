"""Secrets manager abstraction.

Provides a small abstraction to retrieve secrets from environment variables,
local encrypted files (not implemented here), or HashiCorp Vault (if configured).
This is a minimal implementation suitable for local development and extension.
"""
import os
from typing import Optional
import json
from pathlib import Path


class SecretsManager:
    """Simple secrets manager with pluggable backends.

    Current order of resolution:
      1. Environment variable
      2. Local file at `secrets/<path>.json` (simple JSON key-value)
      3. (Future) HashiCorp Vault via `HVAC` if available
    """

    def __init__(self, secrets_dir: Optional[Path] = None):
        if secrets_dir is None:
            secrets_dir = Path(__file__).parent.parent / "secrets"
        self.secrets_dir = Path(secrets_dir)

    def get_secret(self, name: str) -> Optional[str]:
        """Get secret by name.

        The `name` can be a simple key or a path-like key such as "email/sendgrid_api_key".
        """
        # 1) Check environment
        env_key = name.upper().replace("/", "_")
        if env_key in os.environ:
            return os.environ[env_key]

        # 2) Local file
        try:
            # e.g., secrets/email.json with {"sendgrid_api_key": "..."}
            parts = name.split("/")
            if len(parts) >= 2:
                file_name = parts[0] + ".json"
                key = "/".join(parts[1:])
            else:
                file_name = "secrets.json"
                key = parts[0]

            file_path = self.secrets_dir / file_name
            if file_path.exists():
                try:
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    # support nested keys with /
                    if "/" in key:
                        val = data
                        for k in key.split("/"):
                            val = val.get(k, {})
                        return val if isinstance(val, str) else None
                    return data.get(key)
                except Exception:
                    return None
        except Exception:
            return None

        # 3) Vault or other secrets manager could be added here
        return None


__all__ = ["SecretsManager"]
