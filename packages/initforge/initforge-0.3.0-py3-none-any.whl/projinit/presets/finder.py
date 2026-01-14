from projinit.presets import get_preset, list_presets


def find_file_across_presets(filename: str):
    matches = []

    for key in list_presets():
        try:
            preset = get_preset(key)
        except Exception:
            continue

        for f in preset.get("files", []):
            if f.endswith(filename):
                matches.append((key, f))

    return matches
