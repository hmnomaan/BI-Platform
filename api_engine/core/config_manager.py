"""
Configuration management for the API Engine.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from decouple import config
import os


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing config files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "configs"
        
        self.config_dir = Path(config_dir)
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files."""
        # Load shared config
        shared_config_path = self.config_dir / "shared_config.yaml"
        if shared_config_path.exists():
            with open(shared_config_path, 'r') as f:
                self.config.update(yaml.safe_load(f) or {})
        
        # Load environment-specific config
        env_config_path = self.config_dir / self.environment / "api_config.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                # Merge with shared config (env config takes precedence)
                self._deep_merge(self.config, env_config)
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # Common overrides
        if config("API_KEY", default=None):
            self.config.setdefault("api", {})["key"] = config("API_KEY")
        
        if config("DATABASE_URL", default=None):
            self.config.setdefault("database", {})["url"] = config("DATABASE_URL")
        
        # Provider-specific overrides
        providers = ["email", "storage", "signing", "search", "physical_mail"]
        for provider in providers:
            api_key = config(f"{provider.upper()}_API_KEY", default=None)
            if api_key:
                self.config.setdefault("providers", {}).setdefault(provider, {})["api_key"] = api_key
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "providers.email.api_key")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        return self.get(f"providers.{provider_name}", {})
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        keys = key.split(".")
        config_dict = self.config
        
        for k in keys[:-1]:
            if k not in config_dict:
                config_dict[k] = {}
            config_dict = config_dict[k]
        
        config_dict[keys[-1]] = value

