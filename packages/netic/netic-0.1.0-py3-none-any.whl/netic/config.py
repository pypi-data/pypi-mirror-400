from pathlib import Path

CONFIG_PATH = Path.home() / ".netic_key"

def save_key(key: str):
    CONFIG_PATH.write_text(key.strip())

def load_key():
    if not CONFIG_PATH.exists():
        return None
    return CONFIG_PATH.read_text().strip()
