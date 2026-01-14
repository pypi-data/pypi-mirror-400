from pathlib import Path
import yaml


class ConfigError(Exception):
    pass


def load_config(path: str) -> dict:
    cfg_path = Path(path)

    if not cfg_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ConfigError(f"Failed to parse YAML: {e}")

    if not isinstance(data, dict):
        raise ConfigError("Config file must contain a YAML dictionary")

    return data


def normalize_config(cfg: dict, defaults: dict) -> dict:
    """
    Merge user config with defaults.
    Priority: config > defaults
    """
    out = defaults.copy()
    out.update({k: v for k, v in cfg.items() if v is not None})
    return out
