from lib.Singleton import Singleton
from lib import debounce
import json
import logging
from pathlib import Path
from types import MappingProxyType
from lib.observables import ObservableDict

logger = logging.getLogger('Settings')


def update_settings_paths(settings):
    updated = {}
    home_path = str(Path.home())
    for key, value in settings.items():
        if 'directory' in key and value[0] == '~':
            value = value.replace('~', home_path)
        elif isinstance(value, dict):
            value = update_settings_paths(value)
        updated[key] = value
    return updated


DEFUALT_SETTINGS_FILEPATH = Path.cwd() / 'configs/.default-settings.json'


class Settings(metaclass=Singleton):
    _settings = None
    _default_settings = None
    _app = None

    def __init__(self, app, filename='settings.json'):
        self._app = app
        self._filename = filename
        self.load()

    def __getitem__(self, item):
        return self.settings[item]

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __getattribute__(self, item):
        """
        returns attribute from Settings if exists, else delegates to settings<ObservableDict> instance
        :param item:
        :return:
        """
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            return getattr(self.settings, item)

    @property
    def app(self):
        return self._app

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings):
        settings = ObservableDict(settings)
        # save configs if anything changes
        save_debounced = debounce(3)(self.save)
        settings.watch(None, lambda key, old, new: save_debounced())
        self._settings = settings

    @property
    def default_settings(self):
        if not self._default_settings:
            # lazy load default settings
            with open(DEFUALT_SETTINGS_FILEPATH) as f:
                settings = json.load(f)

            settings = update_settings_paths(settings)
            settings = MappingProxyType(settings)
            self._default_settings = settings
        return self._default_settings

    def load(self):
        settings = None
        try:
            with self._app.open(self._filename) as f:
                settings = json.load(f)
        except FileNotFoundError:
            logger.info('{} not found in Application Support. Loading default instead.'.format(self._filename))
        except Exception as e:
            logger.error('Error loading {}'.format(self._filename))
            logger.error(e)

        if not settings:
            settings = self.default_settings

        self.settings = settings

    def save(self):
        settings_dict = self._settings.get_dict()
        with self.app.open(self._filename, 'w') as f:
            json.dump(settings_dict, f)
        logger.info('Saved ' + self._filename)

    def reset(self):
        Path(self.app._application_support, self._filename).unlink(missing_ok=True)
        self.load()
