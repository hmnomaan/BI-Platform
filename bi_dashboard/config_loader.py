"""Dynamic configuration loader for BI Dashboard.

Provides a small utility to load YAML/JSON configs and apply environment overrides.
"""
from pathlib import Path
import os
import yaml
from typing import Any, Dict, Optional


class BIDashboardConfigLoader:
    """Load dashboard configuration with precedence: ENV > env-specific file > shared file > defaults."""

    def __init__(self, configs_dir: Optional[Path] = None, environment: Optional[str] = None):
        if configs_dir is None:
            configs_dir = Path(__file__).parent.parent / "configs"
        self.configs_dir = Path(configs_dir)
        self.environment = environment or os.getenv("ENVIRONMENT", "dev")
        self.config: Dict[str, Any] = {}
        self._load()

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load(self):
        shared = self._load_yaml(self.configs_dir / "shared_config.yaml")
        self.config.update(shared)

        env_file = self.configs_dir / self.environment / "bi_config.yaml"
        env_conf = self._load_yaml(env_file)
        # shallow merge with env taking precedence
        for k, v in env_conf.items():
            if isinstance(v, dict) and isinstance(self.config.get(k), dict):
                self.config[k].update(v)
            else:
                self.config[k] = v

        # Allow environment variable overrides for common keys
        # e.g., BI_DATASOURCE_URL, BI_REFRESH_INTERVAL
        if os.getenv("BI_DATASOURCE_URL"):
            self.config.setdefault("datasource", {})["url"] = os.getenv("BI_DATASOURCE_URL")
        if os.getenv("BI_REFRESH_INTERVAL"):
            try:
                self.config.setdefault("refresh", {})["interval_minutes"] = int(os.getenv("BI_REFRESH_INTERVAL"))
            except ValueError:
                pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        parts = key.split(".")
        val = self.config
        for p in parts:
            if isinstance(val, dict) and p in val:
                val = val[p]
            else:
                return default
        return val


__all__ = ["BIDashboardConfigLoader"]
