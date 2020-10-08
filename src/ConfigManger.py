import json
import logging
from pathlib import Path
from types import MappingProxyType
from .observables import ObservableDict

logger = logging.getLogger(__name__)

_config = None
_default_config = None
_app = None
_config_filename = None


def init(app, config_filename):
    global _app
    global _config_filename

    _app = app
    _config_filename = config_filename

    return load()


def load():
    config = None
    try:
        with _app.open(_config_filename) as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.info('config.json not found in Application Support. Loading default instead.')

    if not config:
        config = default_config()

    global _config
    _config = ObservableDict(config)
    return _config
    # @TODO it's the app's job to attach the observers


def save(config=None):
    if not config:
        config = _config.get_dict()
    with _app.open(_config_filename, 'w') as f:
        json.dump(config, f)
    logger.info('Saved config.json')


def _update_config_paths(config):
    updated = {}
    home_path = str(Path.home())
    for key, value in config.items():
        if 'directory' in key and value[0] == '~':
            value = value.replace('~', home_path)
        elif isinstance(value, dict):
            value = _update_config_paths(value)
        updated[key] = value
    return updated


def config():
    return _config

def default_config():
    global _default_config
    if not _default_config:
        with open(Path.cwd() / '.default_config.json') as f:
            config = json.load(f)
        config = _update_config_paths(config)
        config = MappingProxyType(config)
        _default_config = config

    return _default_config

def reset():
    save(_default_config)

    global _config
    _config = ObservableDict(_default_config)
    return _config # it's the app's job to attach observers


