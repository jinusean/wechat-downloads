from pathlib import Path
import json

def load_config():
    with open('config.json') as f:
        config = json.load(f)

    if config['is_initialized'] == False:
        home_path = Path.home()
        config['wechat_directory'] = str(home_path/config['wechat_directory'])
        config['save_directory'] = str(home_path/config['save_directory'])

    return config


def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)