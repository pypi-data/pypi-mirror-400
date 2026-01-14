"""User configuration management for pykabu"""

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "pykabu"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "default_importance": 0,
    "custom_indices": {},
}


def _ensure_config_dir() -> None:
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load user configuration from file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> None:
    """Save user configuration to file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    config = load_config()
    return config.get(key, default)


def set(key: str, value: Any) -> None:
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


def get_config_path() -> Path:
    """Return the config file path."""
    return CONFIG_FILE


# Custom indices management
def get_custom_indices() -> dict[str, str]:
    """Get user's custom indices configuration."""
    indices = load_config().get("custom_indices", {})
    return dict(indices) if indices else {}


def add_custom_index(code: str, name: str) -> None:
    """Add a custom index to the configuration."""
    config = load_config()
    if "custom_indices" not in config:
        config["custom_indices"] = {}
    config["custom_indices"][code] = name
    save_config(config)


def remove_custom_index(code: str) -> bool:
    """Remove a custom index from configuration. Returns True if removed."""
    config = load_config()
    if "custom_indices" in config and code in config["custom_indices"]:
        del config["custom_indices"][code]
        save_config(config)
        return True
    return False


def clear_custom_indices() -> None:
    """Clear all custom indices."""
    config = load_config()
    config["custom_indices"] = {}
    save_config(config)
