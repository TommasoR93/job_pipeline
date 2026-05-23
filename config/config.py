import yaml
from pathlib import Path

def load_conf():
    conf_path = Path(__file__).parent / "config.yaml"
    if not conf_path.exists():
        raise FileNotFoundError
    with open (conf_path, 'r') as file:
        return yaml.safe_load(file)

