from pathlib import Path
import argparse

from projinit.generator import generate_project_from_base
from projinit.presets import get_preset, list_presets
from projinit.presets.builder import create_preset_interactive
from projinit.presets.store import list_user_presets, load_user_preset
from projinit.validators import validate_python_version, normalize_env_name
from projinit.config import load_config, normalize_config, ConfigError
from projinit.presets.finder import find_file_across_presets


def init():
    root = Path.cwd()
    project_name = root.name

    # -------- CLI args --------
    parser = argparse.ArgumentParser(
        description="Initialize a Python project with a clean structure"
    )
    parser.add_argument("--preset", help="Project preset (base / ml / streamlit)")
    parser.add_argument("--run", help="Run command (e.g. python app.py)")
    parser.add_argument("--config", help="Path to initforge YAML config file")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no files written")
    parser.add_argument(
        "--save-config",
        action="store_true",
        help="Save this setup as .initforge.yaml for reuse",
    )

    args = parser.parse_args()

    print(f"📁 Repo detected: {project_name}")

    # -------- load config --------
    config_data = None
    if args.config:
        try:
            raw_cfg = load_config(args.config)
        except ConfigError as e:
            print(f"❌ {e}")
            return

        defaults = {
            "preset": "base",
            "python": "3.10",
            "env": project_name,
            "run": None,
            "overwrite_readme": True,
        }

        config_data = normalize_config(raw_cfg, defaults)
        print(f"📄 Using config file: {args.config}")

    # -------- presets --------
    base_presets = list_presets()

    # ========== PRESET SELECTION ==========
    if config_data:
        preset_key = config_data["preset"]
        preset = get_preset(preset_key)
        print(f"\n✔ Using preset (config): {preset_key}")

    elif args.preset:
        preset_key = args.preset
        preset = get_preset(preset_key)
        print(f"\n✔ Using preset (flag): {preset_key}")

    else:
        print("\n— Built-in presets —")
        for i, key in enumerate(base_presets, start=1):
            label = get_preset(key)["name"]
            print(f"{i}) {label}")

        user_presets = list_user_presets()

        if user_presets:
            print("\n— Your presets —")
            for i, k in enumerate(user_presets, start=len(base_presets) + 1):
                print(f"{i}) {k}")

        tool_start = len(base_presets) + len(user_presets) + 1

        print("\n— Tools —")
        print(f"{tool_start}) Create preset")
        print(f"{tool_start + 1}) Find file")

        choice = input("Choice [1]: ").strip()

        try:
            index = int(choice) - 1 if choice else 0
        except ValueError:
            index = 0

        total_presets = base_presets + user_presets

        # ---- built-in + user presets ----
        if 0 <= index < len(total_presets):
            preset_key = total_presets[index]

            if preset_key in base_presets:
                preset = get_preset(preset_key)
                print(f"\n✔ Using preset: {preset_key}")
            else:
                preset = load_user_preset(preset_key)
                print(f"\n✔ Using custom preset: {preset_key}")

        # ---- create preset ----
        elif index == tool_start - 1:
            new_key = create_preset_interactive()
            if not new_key:
                preset_key = "base"
                preset = get_preset("base")
            else:
                preset_key = new_key
                preset = load_user_preset(preset_key)
                print(f"\n✔ Using new preset: {preset_key}")

        # ---- find file ----
        elif index == tool_start:
            find_file_across_presets()
            print("\nℹ️ Run initforge again to continue.")
            return

        # ---- fallback ----
        else:
            print("⚠️ Invalid choice. Using base preset.")
            preset_key = "base"
            preset = get_preset("base")

    # ========== PYTHON + ENV ==========
    if config_data:
        python_version = validate_python_version(config_data["python"])
        env_name = normalize_env_name(config_data["env"], project_name)
    else:
        python_version = input("Python version [3.10]: ").strip() or "3.10"
        python_version = validate_python_version(python_version)

        env_name = input(f"Conda env name [{project_name}]: ").strip()
        env_name = normalize_env_name(env_name, project_name)

    # ========== RUN COMMAND + README ==========
    if config_data:
        run_command = config_data["run"] or preset["default_run"]
        overwrite_readme = bool(config_data["overwrite_readme"])
    else:
        run_command = (
            args.run
            or input(f"Run command [{preset['default_run']}]: ").strip()
            or preset["default_run"]
        )

        overwrite = input("Overwrite README.md? (y/n) [y]: ").strip().lower()
        overwrite_readme = overwrite != "n"

    # -------- decide config saving --------
    save_config = bool(args.save_config)

    # ========== GENERATE ==========
    generate_project_from_base(
        project_name=project_name,
        env_name=env_name,
        python_version=python_version,
        run_command=run_command,
        preset_key=preset_key,
        preset=preset,
        overwrite_readme=overwrite_readme,
        save_config=save_config,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("\n🧪 Dry run complete — no files were written.")
        return

    print("\nNext steps:")
    print(f"conda create -n {env_name} python={python_version} -y")
    print(f"conda activate {env_name}")
    print("pip install -r requirements.txt")
