import rumps, json, logging
from pathlib import Path
from .WeChatWatcher import WeChatWatcher
from . import mac_dialogs, utils
from . import ConfigManger

logger = logging.getLogger(__name__)

rumps.debug_mode(True)

class WeChatDownloadsApp(rumps.App):
    _default_config = None

    def __init__(self,name='JamesLee',config='config.json'):
        super().__init__(
            name=name,
            quit_button=None)
        config = ConfigManger.init(self, config)
        self.watch_config(config)

        # initialize Show icon option
        show_icon_menuitem = rumps.MenuItem(title='Show icon', callback=self.toggle_icon)
        show_icon_menuitem.state = config['show_icon']
        self.menu.add(show_icon_menuitem)
        self.update_icon()

        self.wechat_watcher = WeChatWatcher()

    def watch_config(self, config):
        pass # @TOOD

    def run(self):
        logger.info('Starting')
        self.wechat_watcher.start()
        super().run()


    def update_icon(self):
        show_icon_menuitem = self.menu.get('Show icon')
        config = ConfigManger.config()
        if config['show_icon']:
            self.icon = config['icon']
            self.title = None
            show_icon_menuitem.state = 1
        else:
            self.icon = None
            self.title = config['title']
            show_icon_menuitem.state = -1

    def toggle_icon(self, _):
        config = ConfigManger.config()
        config['show_icon'] = not config['show_icon']


    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        self.update_directory('save_directory', 'Select directory to save files')

    @rumps.clicked('Change WeChat directory')
    def set_wechat_dir(self, _):
        self.update_directory('wechat_directory', 'Select WeChat directory')


    @rumps.clicked('Reset settings')
    def reset_preferences(self, _):
        res = mac_dialogs.dialog(message='Are you sure you want to reset your settings?', title='WeChat Downloads')
        if not res:
            return
        config = ConfigManger.reset()
        self.watch_config(config)
        mac_dialogs.confirm(message='Settings succesfully updated!', title='WeChats Download')

    @rumps.clicked('Quit')
    def quit(self, _):
        self.wechat_watcher.stop()
        rumps.quit_application()

    def update_directory(self, config_key, message=None):
        config = ConfigManger.config()
        original_dir = config[config_key]
        new_dir = mac_dialogs.directory(original_dir, message)
        print(original_dir, new_dir)

        if not new_dir or Path(original_dir) == Path(new_dir):
            return False

        config[config_key] = new_dir
        mac_dialogs.confirm('Directory successfully changed!', title='WeChat Downloads')
        return True
