"""
Preset definitions for initforge.

Each preset describes:
- folder structure
- default files
- default run command
- default dependencies
"""

PRESETS = {
    "base": {
        "name": "Base",
        "description": "Basic Python project structure",
        "folders": [
            "src/{project_name}",
            "tests",
        ],
        "files": [
            "src/{project_name}/__init__.py",
            "src/{project_name}/logger.py",
        ],
        "requirements": [],
        "default_run": "python app.py",
    },

    "ml": {
        "name": "ML / Data Science",
        "description": "Machine learning project structure",
        "folders": [
            "data/raw",
            "data/processed",
            "notebooks",
            "src/{project_name}",
            "tests",
        ],
        "files": [
            "src/{project_name}/__init__.py",
            "src/{project_name}/train.py",
            "src/{project_name}/predict.py",
            "src/{project_name}/logger.py",
        ],
        "requirements": [
            "numpy",
            "pandas",
            "scikit-learn",
            "matplotlib",
        ],
        "default_run": "python src/{project_name}/train.py",
    },

    "streamlit": {
        "name": "Streamlit App",
        "description": "Streamlit-based application",
        "folders": [
            "src/{project_name}",
            "assets",
            "tests",
        ],
        "files": [
            "src/{project_name}/__init__.py",
            "src/{project_name}/app.py",
            "src/{project_name}/logger.py",
        ],
        "requirements": [
            "streamlit",
            "python-dotenv",
        ],
        "default_run": "streamlit run src/{project_name}/app.py",
    },
}


def get_preset(name: str):
    """
    Return preset config by name.
    Falls back to base preset.
    """
    return PRESETS.get(name, PRESETS["base"])


def list_presets():
    """
    List available preset keys.
    """
    return list(PRESETS.keys())
