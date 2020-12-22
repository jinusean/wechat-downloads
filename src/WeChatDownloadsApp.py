import rumps, logging, time, os
from pathlib import Path
from src.watchers import WeChatWatcher
from lib import mac_dialogs
from src.Settings import Settings
from src.managers import WatchersManager

logger = logging.getLogger('WeChatDownloadsApp')


class WeChatDownloadsApp(rumps.App):
    def __init__(self, name, settings):
        super().__init__(name=name, quit_button=None)
        self.settings = Settings(self, settings)
        self.watch_settings(self.settings)
        self.icon = self.settings['icon']
        self.watchers_manager = WatchersManager(self, os.getenv('SYNC_FILENAME'))

        more_options = rumps.MenuItem(title='More Options')
        self.menu.add(more_options)

        self.wechat_watcher = WeChatWatcher(self.settings['wechat_directory'])

    def watch_settings(self, settings):
        def on_wechat_directory(old, new):
            self.wechat_watcher.stop()
            self.wechat_watcher = WeChatWatcher(new)
            self.wechat_watcher.start()

        settings.watch('wechat_directory', on_wechat_directory)

    def run(self):
        logger.info('Starting')
        self.wechat_watcher.start()
        super().run()


    def update_directory(self, settings_key, message=None):
        original_dir = self.settings[settings_key]
        new_dir = mac_dialogs.directory(original_dir, message)

        if not new_dir or Path(original_dir) == Path(new_dir):
            logger.debug('update_directory: ' + settings_key + ' cancelled')
            return False

        logger.debug('update_directory: ' + settings_key + ' updated to ' + new_dir)
        self.settings[settings_key] = new_dir
        mac_dialogs.confirm('Directory successfully changed!', title='WeChat Downloads')
        return True

    @rumps.clicked('More Options', 'Change save directory')
    def set_save_dir(self, _):
        self.update_directory('save_directory', 'Select directory to save files')

    @rumps.clicked('More Options', 'Change WeChat directory')
    def set_wechat_dir(self, _):
        self.update_directory('wechat_directory', 'Select WeChat directory')

    @rumps.clicked('More Options', 'Reset Settings')
    def reset_preferences(self, _):
        title= 'WeChats Download: Reset Settings'
        res = mac_dialogs.dialog(message='Are you sure you want to reset your settingss?', title=title)
        if not res:
            return
        settings = Settings()
        settings.reset()
        self.watch_settings(settings)
        mac_dialogs.confirm(message='Settings succesfully updated!', title=title)

    @rumps.clicked('Sync all')
    def sync_all(self, _):
        count = self.watchers_manager.sync_all()
        message = 'Synced {} files to:\n {}!'.format(count, self.settings['save_directory'])
        mac_dialogs.confirm(message=message, title='WeChats Download: Sync All')

    @rumps.clicked('Quit')
    def quit(self, _):
        self.wechat_watcher.stop()
        self.watchers_manager.save()
        rumps.quit_application()
