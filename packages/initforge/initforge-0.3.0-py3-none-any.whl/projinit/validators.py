def validate_python_version(version: str, default="3.10"):
    allowed = ["3.5","3.6","3.7","3.8", "3.9", "3.10", "3.11", "3.12"]

    if version in allowed:
        return version

    print(f"⚠️ Invalid Python version '{version}'")
    print(f"Allowed versions: {', '.join(allowed)}")

    retry = input(f"Enter Python version again [{default}]: ").strip()
    if retry in allowed:
        return retry

    print(f"⚠️ Using default Python version {default}")
    return default


def normalize_env_name(name: str, fallback: str):
    return name.strip() or fallback
