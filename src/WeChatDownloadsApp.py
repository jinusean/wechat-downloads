import rumps
import json
import logging
from pathlib import Path
import copy
from .WeChatWatcherThread import WeChatWatcherThread
from . import mac_dialogs, utils

logger = logging.getLogger(__name__)


class WeChatDownloadsApp(rumps.App):
    def __init__(self):
        super().__init__(
            name='JamesLee',
            quit_button=None)
        config = self.load_config()  # config must be loaded before all else

        # initialize Show icon option
        show_icon_menuitem = rumps.MenuItem(title='Show icon', callback=self.toggle_icon)
        show_icon_menuitem.state = config['show_icon']
        self.menu.add(show_icon_menuitem)
        self.update_icon()

        self.wechat_watcher_thread = WeChatWatcherThread(config)
        self.wechat_watcher_thread.daemon = True

    def set_config(self, new_config, save=True):


        default_config = self.get_default_config()
        utils.validate_config(default_config, new_config)

        if hasattr(self, 'config'):
            current_config = self.config
            if new_config['show_icon'] != current_config['show_icon']:
                self.update_icon()
            if new_config['wechat_directory'] != current_config['wechat_directory']:
                self.wechat_watcher_thread.restart_watcher()

        self._config = new_config

        if save:
            self.save_config()

    def run(self):
        logger.info('Starting')
        self.wechat_watcher_thread.start()
        super().run()

    def save_config(self):
        with self.open('config.json', 'w') as f:
            json.dump(self._config, f)
        logger.info('Saved config.json')


    def get_config(self):
        return copy.deepcopy(self._config)

    def get_default_config(self):
        if not hasattr(self, '_default_config'):
            self._default_config = utils.load_default_config()
        return copy.deepcopy(self._default_config)

    def update_icon(self):
        show_icon_menuitem = self.menu.get('Show icon')
        config = self.get_config()
        if config['show_icon']:
            self.icon = config['icon']
            self.title = None
            show_icon_menuitem.state = 1
        else:
            self.icon = None
            self.title = config['title']
            show_icon_menuitem.state = -1

    def load_config(self):
        try:
            with self.open('config.json') as f:
                config = json.load(f)
                self.set_config(config, False)
                logger.info('Loaded config.json')
            return config
        except Exception as e:
            logger.warning(
                'Error loading config.json from Application support. \n\tLoading .default_config.json instead')
            logger.warning(e)

        default_config = self.get_default_config()
        self.set_config(default_config)
        logger.info('Loaded default config')
        return default_config

    def toggle_icon(self, _):
        config = self.get_config()
        config['show_icon'] = not config['show_icon']
        self.set_config(config)

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
        self.set_config(self.get_default_config())
        mac_dialogs.confirm(message='Settings succesfully updated!', title='WeChats Download')

    @rumps.clicked('Quit')
    def quit(self, _):
        if hasattr(self, 'wechat_watcher_thread'):
            self.wechat_watcher_thread.stop()
        rumps.quit_application()

    def update_directory(self, config_key, message=None):
        config = self.get_config()
        original_dir = config[config_key]
        new_dir = mac_dialogs.directory(original_dir, message)

        if new_dir and original_dir == new_dir:
            return False

        config[config_key] = new_dir

        self.set_config(config)
        mac_dialogs.confirm('Directory successfully changed!', title='WeChat Downloads')
        return True
