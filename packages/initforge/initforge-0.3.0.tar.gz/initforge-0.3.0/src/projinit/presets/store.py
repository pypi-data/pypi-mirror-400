from pathlib import Path
import yaml


def get_user_preset_dir() -> Path:
    """
    Returns ~/.initforge/presets
    Creates it if missing.
    """
    base = Path.home() / ".initforge" / "presets"
    base.mkdir(parents=True, exist_ok=True)
    return base


def list_user_presets():
    """
    Returns list of preset names (without .yaml)
    """
    base = get_user_preset_dir()
    return [p.stem for p in base.glob("*.yaml")]


def load_user_preset(name: str) -> dict:
    """
    Load a user preset by name.
    """
    path = get_user_preset_dir() / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Preset '{name}' not found")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_user_preset(name: str, data: dict):
    """
    Save a preset to ~/.initforge/presets/{name}.yaml
    """
    path = get_user_preset_dir() / f"{name}.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    return path
