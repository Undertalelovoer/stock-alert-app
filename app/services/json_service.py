import json
from pathlib import Path


def load_json(path: str, default):
    file_path = Path(path)

    if not file_path.exists():
        return default

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)