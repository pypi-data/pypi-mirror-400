"""
Runtime configuration manager for insyt-secure.
Handles persistent configuration that survives restarts.
"""
import os
import json
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

# Configuration file path
CONFIG_FILE = Path('./data/runtime_config.json')


class RuntimeConfig:
    """Singleton runtime configuration manager."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from file, create if doesn't exist."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load runtime config: {e}")
                self._config = {}
        else:
            # Initialize with defaults
            self._config = self._create_defaults()
            self._save_config()
    
    def _create_defaults(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'secret_key': secrets.token_hex(32),  # Generate once, persist forever
            'web_config': {
                'port': 8080,
                'host': '0.0.0.0',  # Bind to all interfaces for remote access
                'enabled': True
            },
            'db_paths': {
                'audit_db': './data/audit_logs.db',
                'auth_db': './data/auth.db'
            },
            'env_presets': {
                'auto_apply_enabled': True,  # Auto-apply preset on startup
                'active_preset_id': None     # ID of preset to auto-apply (null = none)
            }
        }
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error: Failed to save runtime config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value and persist."""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the nested key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_config()
    
    def get_secret_key(self) -> str:
        """Get persistent secret key (auto-generated on first run)."""
        secret_key = self.get('secret_key')
        if not secret_key:
            # Generate new secret key if missing
            secret_key = secrets.token_hex(32)
            self.set('secret_key', secret_key)
        return secret_key
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web server configuration."""
        return self.get('web_config', {
            'port': 8080,
            'host': '0.0.0.0',  # Bind to all interfaces for remote access
            'enabled': True
        })
    
    def set_web_config(self, port: int = None, host: str = None, enabled: bool = None):
        """Update web server configuration."""
        current = self.get_web_config()
        
        if port is not None:
            current['port'] = port
        if host is not None:
            current['host'] = host
        if enabled is not None:
            current['enabled'] = enabled
        
        self.set('web_config', current)
    
    def get_db_paths(self) -> Dict[str, str]:
        """Get database paths."""
        return self.get('db_paths', {
            'audit_db': './data/audit_logs.db',
            'auth_db': './data/auth.db'
        })
    
    def get_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project-specific configuration."""
        return self.get(f'projects.{project_id}')
    
    def set_project_config(self, project_id: str, config: Dict[str, Any]):
        """Set project-specific configuration."""
        self.set(f'projects.{project_id}', config)


# Singleton instance
_runtime_config = RuntimeConfig()


def get_secret_key() -> str:
    """Get persistent secret key."""
    # Priority: ENV VAR > Runtime Config > Auto-generated
    return os.getenv('SECRET_KEY') or _runtime_config.get_secret_key()


def get_web_config() -> Dict[str, Any]:
    """Get web server configuration."""
    config = _runtime_config.get_web_config()
    
    # Environment variables override file config
    if os.getenv('WEB_INTERFACE_PORT'):
        config['port'] = int(os.getenv('WEB_INTERFACE_PORT'))
    if os.getenv('WEB_INTERFACE_HOST'):
        config['host'] = os.getenv('WEB_INTERFACE_HOST')
    if os.getenv('WEB_INTERFACE_ENABLED'):
        config['enabled'] = os.getenv('WEB_INTERFACE_ENABLED', 'true').lower() == 'true'
    
    return config


def get_db_paths() -> Dict[str, str]:
    """Get database paths."""
    paths = _runtime_config.get_db_paths()
    
    # Environment variables override file config
    if os.getenv('AUDIT_DB_PATH'):
        paths['audit_db'] = os.getenv('AUDIT_DB_PATH')
    if os.getenv('AUTH_DB_PATH'):
        paths['auth_db'] = os.getenv('AUTH_DB_PATH')
    
    return paths


def save_web_config(port: int = None, host: str = None, enabled: bool = None):
    """Save web server configuration."""
    _runtime_config.set_web_config(port=port, host=host, enabled=enabled)
