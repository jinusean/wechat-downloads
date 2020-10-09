import rumps, logging
from pathlib import Path
from .WeChatWatcher import WeChatWatcher
from . import mac_dialogs
from . import SettingsManager

logger = logging.getLogger(__name__)

rumps.debug_mode(True)


class WeChatDownloadsApp(rumps.App):
    def __init__(self, name='JamesLee', settings='settingss.json'):
        super().__init__(
            name=name,
            quit_button=None)
        settings = SettingsManager.init(self, settings)
        self.watch_settings(settings)

        # initialize Show icon option
        show_icon_menuitem = rumps.MenuItem(title='Show icon', callback=self.toggle_icon)
        show_icon_menuitem.state = settings['show_icon']
        self.menu.add(show_icon_menuitem)
        self.update_icon()

        self.wechat_watcher = WeChatWatcher()

    def watch_settings(self, settings):
        def on_show_icon(old, new):
            self.update_icon()

        def on_wechat_directory(old, new):
            self.wechat_watcher.stop()
            self.wechat_watcher.start()

        settings.watch('show_icon', on_show_icon)
        settings.watch('wechat_directory', on_wechat_directory)

    def run(self):
        logger.info('Starting')
        self.wechat_watcher.start()
        super().run()

    def update_icon(self):
        show_icon_menuitem = self.menu.get('Show icon')
        settings = SettingsManager.settings()
        if settings['show_icon']:
            self.icon = settings['icon']
            self.title = None
            show_icon_menuitem.state = 1
        else:
            self.icon = None
            self.title = settings['title']
            show_icon_menuitem.state = -1

    def toggle_icon(self, _):
        settings = SettingsManager.settings()
        settings['show_icon'] = not settings['show_icon']

    def update_directory(self, settings_key, message=None):
        settings = SettingsManager.settings()
        original_dir = settings[settings_key]
        new_dir = mac_dialogs.directory(original_dir, message)

        if not new_dir or Path(original_dir) == Path(new_dir):
            logger.debug('update_directory:', settings_key, 'cancelled')
            return False

        settings[settings_key] = new_dir
        mac_dialogs.confirm('Directory successfully changed!', title='WeChat Downloads')
        logger.debug('update_directory:', settings_key, 'updated to ' + new_dir)
        return True

    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        self.update_directory('save_directory', 'Select directory to save files')

    @rumps.clicked('Change WeChat directory')
    def set_wechat_dir(self, _):
        self.update_directory('wechat_directory', 'Select WeChat directory')

    @rumps.clicked('Reset settingss')
    def reset_preferences(self, _):
        res = mac_dialogs.dialog(message='Are you sure you want to reset your settingss?', title='WeChat Downloads')
        if not res:
            return
        settings = SettingsManager.reset()
        self.watch_settings(settings)
        mac_dialogs.confirm(message='Settings succesfully updated!', title='WeChats Download')

    @rumps.clicked('Quit')
    def quit(self, _):
        self.wechat_watcher.stop()
        rumps.quit_application()
