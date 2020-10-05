from pathlib import Path
import json


def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)


def update_config_paths(config):
    updated = {}
    home_path = str(Path.home())
    for key, value in config.items():
        if 'directory' in key and value[0] == '~':
            value = value.replace('~', home_path)
        elif isinstance(value, dict):
            value = update_config_paths(value)
        updated[key] = value
    return updated


def load_default_config():
    with open(Path.cwd() / '.default_config.json') as f:
        config = json.load(f)
    return update_config_paths(config)


def validate_config(default, config):
    for key, default_value in default.items():
        if key not in config:
            raise Exception('Invalid config')
        if isinstance(default_value, dict):
            validate_config(default_value, config[key])
        if key == 'icon' and not Path(config[key]).exists():
            raise Exception('Invalid config icon')
