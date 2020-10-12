import rumps, logging
from pathlib import Path
from src.watchers import WeChatWatcher
from lib import mac_dialogs
from src.Settings import Settings
from src.Manager import Manager
from src import utils

logger = logging.getLogger('WeChatDownloadsApp')


class WeChatDownloadsApp(rumps.App):
    def __init__(self, name, settings):
        super().__init__(name=name, quit_button=None)
        self.settings = Settings(self, settings)

        self.watch_settings(self.settings)
        self.manager = Manager(self)

        # initialize Show icon option
        show_icon_menuitem = rumps.MenuItem(title='Daddy', callback=self.toggle_icon)
        autosync_menuitem = rumps.MenuItem(title='Autosync', callback=self.toggle_icon)

        more_options = rumps.MenuItem(title='More Options')
        more_options.add(show_icon_menuitem)
        more_options.add(autosync_menuitem)
        self.menu.add(more_options)
        self.update_icon()  # update show_icon menu
        self.update_autosync()  # update autosync menu

        self.wechat_watcher = WeChatWatcher(self.settings['wechat_directory'])

    def watch_settings(self, settings):
        def on_wechat_directory(old, new):
            self.wechat_watcher.stop()
            self.wechat_watcher = WeChatWatcher(new)
            self.wechat_watcher.start()

        settings.watch('show_icon', lambda old, new: self.update_icon())
        settings.watch('wechat_directory', on_wechat_directory)
        settings.watch('autosync', lambda old, new: self.update_autosync())

    def run(self):
        logger.info('Starting')
        self.wechat_watcher.start()
        super().run()

    def update_autosync(self):
        autosync_menuitem = self.menu.get('More Options').get('Autosync')
        autosync_menuitem.state = 1 if self.settings['autosync'] else 0

    def update_icon(self):
        show_icon_menuitem = self.menu.get('More Options').get('Daddy')
        settings = self.settings
        if settings['show_icon']:
            self.icon = settings['icon']
            self.title = None
            show_icon_menuitem.state = 1
        else:
            self.icon = None
            self.title = settings['title']
            show_icon_menuitem.state = 0

    def toggle_icon(self, _):
        key = dict(Daddy='show_icon', Autosync='autosync')[_.title]
        self.settings[key] = not self.settings[key]

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

    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        self.update_directory('save_directory', 'Select directory to save files')

    @rumps.clicked('Change WeChat directory')
    def set_wechat_dir(self, _):
        self.update_directory('wechat_directory', 'Select WeChat directory')

    @rumps.clicked('More Options', 'Reset settingss')
    def reset_preferences(self, _):
        res = mac_dialogs.dialog(message='Are you sure you want to reset your settingss?', title='WeChat Downloads')
        if not res:
            return
        settings = Settings()
        settings.reset()
        self.watch_settings(settings)
        mac_dialogs.confirm(message='Settings succesfully updated!', title='WeChats Download')

    @rumps.clicked('Sync all')
    def sync_all(self, _):
        count = 0
        for dir in self.manager.get_dirs_by_cls('UserWatcher'):
            for file in utils.iter_files(dir):
                if utils.validate_file_and_copy(file):
                    count += 1
        if count == 0:
            message = 'No files to copy...'
        else:
            message = 'Copied {} files to:\n{}!'.format(count, Settings()['save_directory'])
        mac_dialogs.confirm(message=message, title="WeChat Downloads")

    @rumps.clicked('Quit')
    def quit(self, _):
        self.wechat_watcher.stop()
        rumps.quit_application()
