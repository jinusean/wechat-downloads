import json
import logging
from pathlib import Path
from types import MappingProxyType
from observables import ObservableDict

logger = logging.getLogger(__name__)

_settings = None
_default_settings = None
_default_settings_filepath = Path.cwd() / 'configs/.default-settings.json'
_app = None


def init(app, config_filename):
    global _app
    global _settings_filename

    _app = app
    _settings_filename = config_filename

    return load()


def load():
    settings = None
    try:
        with _app.open(_settings_filename) as f:
            settings = json.load(f)
    except FileNotFoundError:
        logger.info('configs.json not found in Application Support. Loading default instead.')
    except Exception as e:
        logger.error('Error loading configs.json')
        logger.error(e)

    if not settings:
        settings = default_settings()

    return set(settings)


def save(settings=None):

    if not settings:
        settings = _settings.get_dict()
    with _app.open(_settings_filename, 'w') as f:
        json.dump(settings, f)
    logger.info('Saved ' + _settings_filename)


def _update_settings_paths(settings):
    updated = {}
    home_path = str(Path.home())
    for key, value in settings.items():
        if 'directory' in key and value[0] == '~':
            value = value.replace('~', home_path)
        elif isinstance(value, dict):
            value = _update_settings_paths(value)
        updated[key] = value
    return updated


def settings():
    return _settings


def default_settings():
    global _default_settings
    if not _default_settings:
        # lazy load default settings
        with open(_default_settings_filepath) as f:
            settings = json.load(f)

        settings = _update_settings_paths(settings)
        settings = MappingProxyType(settings)
        _default_settings = settings
    return _default_settings


def set(settings):
    settings = ObservableDict(settings)
    # save configs if anything changes
    settings.watch(None, lambda key, old, new: save())

    global _settings
    _settings = settings

    return settings


def reset():
    # copy default configs to application_suppert/configs.json
    Path(_app._application_support, _settings_filename).unlink(missing_ok=True)
    return load()
