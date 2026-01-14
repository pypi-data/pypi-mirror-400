from projinit.presets.store import save_user_preset


def create_preset_interactive():
    print("\n🧩 Create a new preset\n")

    key = input("Preset key (e.g. flask, api, cli): ").strip().lower()
    if not key:
        print("❌ Preset key required.")
        return None

    name = input("Display name [My Preset]: ").strip() or "My Preset"

    print("\n📁 Folders (comma separated)")
    folders_raw = input("e.g. src/{project_name}, tests: ").strip()
    folders = [f.strip() for f in folders_raw.split(",") if f.strip()]

    print("\n📄 Files (comma separated)")
    files_raw = input("e.g. src/{project_name}/app.py, .env: ").strip()
    files = [f.strip() for f in files_raw.split(",") if f.strip()]

    print("\n📦 Requirements (comma separated)")
    req_raw = input("e.g. flask, requests: ").strip()
    requirements = [r.strip() for r in req_raw.split(",") if r.strip()]

    default_run = input(
        "\n▶ Default run command [python src/{project_name}/app.py]: "
    ).strip() or "python src/{project_name}/app.py"

    preset = {
        "name": name,
        "folders": folders,
        "files": files,
        "requirements": requirements,
        "default_run": default_run,
    }

    path = save_user_preset(key, preset)

    print(f"\n✅ Preset '{key}' saved!")
    print(f"📍 Location: {path}")

    return key
