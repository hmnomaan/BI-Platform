import os
from bi_dashboard.config_loader import BIDashboardConfigLoader
from pathlib import Path


def test_config_loader_default():
    loader = BIDashboardConfigLoader()
    # basic keys should exist (shared_config may vary); ensure `get` returns default when missing
    assert loader.get("nonexistent.key", "xyz") == "xyz"


def test_env_override(tmp_path, monkeypatch):
    conf_dir = tmp_path / "configs"
    conf_dir.mkdir()
    # create shared_config.yaml
    shared = conf_dir / "shared_config.yaml"
    shared.write_text("server:\n  port: 9000\n")

    # set ENV to point to tmp config directory
    loader = BIDashboardConfigLoader(configs_dir=conf_dir)
    # ensure default port loaded
    assert loader.get("server.port") == 9000

    # override via env
    monkeypatch.setenv("BI_REFRESH_INTERVAL", "15")
    loader2 = BIDashboardConfigLoader(configs_dir=conf_dir)
    assert loader2.get("refresh.interval_minutes") == 15
