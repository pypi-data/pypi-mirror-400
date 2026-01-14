from projinit.presets.store import load_user_preset, list_user_presets


# ---------------------------
# Built-in presets
# ---------------------------

_BUILTIN_PRESETS = {
    "base": {
        "name": "Base",
        "folders": [
            "src/{project_name}",
            "tests",
        ],
        "files": [
            "src/{project_name}/__init__.py",
            "tests/__init__.py",
        ],
        "requirements": [],
        "default_run": "python src/{project_name}/main.py",
    },

    "ml": {
        "name": "ML / Data Science",
        "folders": [
            "src/{project_name}",
            "data",
            "notebooks",
            "tests",
        ],
        "files": [
            "src/{project_name}/train.py",
            "src/{project_name}/__init__.py",
            "tests/__init__.py",
        ],
        "requirements": [
            "numpy",
            "pandas",
            "scikit-learn",
        ],
        "default_run": "python src/{project_name}/train.py",
    },

    "streamlit": {
        "name": "Streamlit App",
        "folders": [
            "src/{project_name}",
            "assets",
            "tests",
        ],
        "files": [
            "src/{project_name}/app.py",
            "src/{project_name}/__init__.py",
        ],
        "requirements": [
            "streamlit",
        ],
        "default_run": "streamlit run src/{project_name}/app.py",
    },
}


# ---------------------------
# Public API
# ---------------------------

def list_presets():
    """
    Returns all available preset keys
    (built-in + user presets)
    """
    user = list_user_presets()
    return list(_BUILTIN_PRESETS.keys()) + user


def get_preset(key: str) -> dict:
    """
    Load a preset by key.
    Priority:
    1. Built-in presets
    2. User presets (~/.initforge/presets/*.yaml)
    """
    # 1️⃣ built-in
    if key in _BUILTIN_PRESETS:
        preset = _BUILTIN_PRESETS[key].copy()
        preset["key"] = key
        return preset

    # 2️⃣ user preset
    user = load_user_preset(key)
    if user:
        user = user.copy()
        user["key"] = key
        return user

    # ❌ not found
    raise KeyError(f"Preset '{key}' not found")
