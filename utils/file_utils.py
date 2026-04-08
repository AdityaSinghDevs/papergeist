import json
import os

def read_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except:
        return default

def write_json(path:str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)