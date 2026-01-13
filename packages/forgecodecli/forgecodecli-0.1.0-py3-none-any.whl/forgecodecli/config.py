from pathlib import Path
import json


CONFIG_DIR = Path.home() / ".forgecodecli"
CONFIG_FILE = CONFIG_DIR / "config.json"

def config_exists()-> bool:
    return CONFIG_FILE.exists()

def load_config()-> dict:
    if not config_exists():
        return {}
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    

def save_config(config: dict):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
        
def delete_config():
    if config_exists():
        CONFIG_FILE.unlink()
        