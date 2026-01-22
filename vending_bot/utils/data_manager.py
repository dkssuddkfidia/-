import json
import os

BASE = "data"

def load_json(name):
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(name, data):
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
