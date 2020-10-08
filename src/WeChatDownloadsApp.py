import rumps
import json
import logging
import copy
from .WeChatWatcherThread import WeChatWatcherThread
from . import mac_dialogs, utils
from .observables import ObservableDict
from multiprocessing.managers import BaseManager, NamespaceProxy



logger = logging.getLogger(__name__)


class ConfigManager(BaseManager):
    pass

class ObservableDictProxy(NamespaceProxy):
    _exposed_ = ('__getitem__', '__getattribute__')


ConfigManager.register('ObservableDict', ObservableDict, ObservableDictProxy)



class WeChatDownloadsApp(rumps.App):
    _config_filename = 'config.json'
    _default_config = None
    _config = None

    def __init__(self):
        super().__init__(
            name='JamesLee',
            quit_button=None)
        self.config_manager = ConfigManager()
        self.config_manager.start()
        self.load_config()  # config must be loaded before all else

        # initialize Show icon option
        show_icon_menuitem = rumps.MenuItem(title='Show icon', callback=self.toggle_icon)
        show_icon_menuitem.state = self.config['show_icon']
        self.menu.add(show_icon_menuitem)
        self.update_icon()

        self.wechat_watcher_thread = WeChatWatcherThread(self.config)
        self.wechat_watcher_thread.daemon = True

    @property
    def default_config(self):
        if not self._default_config:
            self._default_config = utils.load_default_config()
        return copy.deepcopy(self._default_config)

    @default_config.setter
    def default_config(self, default_config):
        self._default_config = default_config

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    def run(self):
        logger.info('Starting')
        # self.wechat_watcher_thread.start()
        super().run()

    def save_config(self):
        config = self.config.target  # get dict instance of config
        with self.open(self._config_filename, 'w') as f:
            json.dump(config, f)
        logger.info('Saved config.json')

    def update_icon(self):
        show_icon_menuitem = self.menu.get('Show icon')
        if self.config['show_icon']:
            self.icon = self.config['icon']
            self.title = None
            show_icon_menuitem.state = 1
        else:
            self.icon = None
            self.title = self.config['title']
            show_icon_menuitem.state = -1

    def load_config(self):
        config = None
        try:
            with self.open(self._config_filename) as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.info('config.json not found in Application Support. Loading default instead.')

        if not config:
            config = self.default_config
        self.config = self.config_manager.ObservableDict(config)

    def toggle_icon(self, _):
        config = self.config
        config.set('show_icon', not config.get('show_icon'))

    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        self.update_directory('save_directory', 'Select directory to save files')

    @rumps.clicked('Change WeChat directory')
    def set_wechat_dir(self, _):
        is_new_dir = self.update_directory('wechat_directory', 'Select WeChat directory')
        if is_new_dir:
            self.wechat_watcher_thread.restart_watcher()

    @rumps.clicked('Reset settings')
    def reset_preferences(self, _):
        res = mac_dialogs.dialog(message='Are you sure you want to reset your settings?', title='WeChat Downloads')
        if not res:
            return
        self.config = self.default_config
        mac_dialogs.confirm(message='Settings succesfully updated!', title='WeChats Download')

    @rumps.clicked('Quit')
    def quit(self, _):
        if hasattr(self, 'wechat_watcher_thread'):
            self.wechat_watcher_thread.stop()
        rumps.quit_application()

    def update_directory(self, config_key, message=None):
        original_dir = self.config[config_key]
        new_dir = mac_dialogs.directory(original_dir, message)

        if new_dir and original_dir == new_dir:
            return False

        self.config[config_key] = new_dir
        mac_dialogs.confirm('Directory successfully changed!', title='WeChat Downloads')
        return True
