from pathlib import Path
from importlib import resources
import yaml


TEMPLATE_PACKAGE = "projinit"
TEMPLATE_BASE = ("templates", "base")


def _read(rel_path: str) -> str:
    return (
        resources.files(TEMPLATE_PACKAGE)
        .joinpath(*TEMPLATE_BASE, rel_path)
        .read_text(encoding="utf-8")
    )


def _write(path: Path, content: str, overwrite: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _ensure_file(path: Path, content: str = ""):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _save_config(root: Path, data: dict):
    cfg_path = root / ".initforge.yaml"
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)
    print("💾 Config saved to .initforge.yaml")


def generate_project_from_base(
    project_name,
    env_name,
    python_version,
    run_command,
    preset_key: str,
    preset: dict,
    overwrite_readme=True,
    save_config=True,
    dry_run=False,
):
    root = Path.cwd()

    # ---------- DRY RUN ----------
    if dry_run:
        print("\n🧪 DRY RUN — preview only\n")

    # -------- folders --------
    for folder in preset.get("folders", []):
        folder_path = root / folder.format(project_name=project_name)
        if dry_run:
            print(f"Would create folder: {folder_path}")
        else:
            _ensure_dir(folder_path)

    # -------- files --------
    for file in preset.get("files", []):
        file_path = root / file.format(project_name=project_name)
        if dry_run:
            print(f"Would create file: {file_path}")
        else:
            _ensure_file(file_path)

    # -------- gitignore --------
    if dry_run:
        print("Would write: .gitignore")
    else:
        _write(root / ".gitignore", _read(".gitignore.txt"), overwrite=False)

    # -------- requirements.txt --------
    req_path = root / "requirements.txt"
    requirements = preset.get("requirements", [])

    if dry_run:
        print("Would write: requirements.txt")
    else:
        if not req_path.exists() or not req_path.read_text().strip():
            req_path.write_text("\n".join(requirements) + "\n", encoding="utf-8")

    # -------- README --------
    readme_template = _read("README.md.txt")
    readme = readme_template.format(
        project_name=project_name,
        env_name=env_name,
        python_version=python_version,
        run_command=run_command,
    )

    if dry_run:
        print("Would write: README.md")
    else:
        _write(root / "README.md", readme, overwrite=overwrite_readme)

    # -------- SAVE CONFIG (only if flag used) --------
    if not dry_run and save_config:
        cfg = {
            "preset": preset_key,
            "python": python_version,
            "env": env_name,
            "run": run_command,
            "overwrite_readme": overwrite_readme,
        }
        _save_config(root, cfg)

    if not dry_run:
        print("\n✔ Project structure created")
        print("✔ Preset applied successfully")
