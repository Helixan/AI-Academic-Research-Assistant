import yaml
import os

DEFAULT_CONFIG_PATH = "config/config.yaml"

def load_config(path: str = DEFAULT_CONFIG_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config
