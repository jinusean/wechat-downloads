import rumps
from multiprocessing import Pipe
import shutil
from .utils import load_config, save_config
from .TkinterProcess import TkinterProcess
import logging
from .WeChatWatcherThread import WeChatWatcherThread

logger = logging.getLogger(__name__)

class WeChatDownloadsApp(rumps.App):
    def __init__(self, name):
        self._default_icon = 'assets/icon.icns'
        super().__init__(name, icon=self._default_icon, quit_button=None)
        self.config = load_config()
        self.wechat_watcher_thread = WeChatWatcherThread(self.config)
        self.wechat_watcher_thread.daemon = True

    def run(self):
        logger.info('starting')
        self.wechat_watcher_thread.start()
        super().run()

    def get_tk_process(self):
        parent_conn, child_conn = Pipe()
        tk = TkinterProcess(child_conn)
        tk.daemon = True
        tk.start()
        return tk, parent_conn

    def ask_directory(self, config_key):
        tk, pipe = self.get_tk_process()

        old_dir = self.config[config_key]
        pipe.send(('askdirectory', old_dir))
        new_dir = pipe.recv()

        is_new_dir = new_dir != old_dir
        if is_new_dir:
            self.config[config_key] = new_dir
            save_config(self.config)

        pipe.send(('showinfo', 'Save directory successfully updated!'))
        pipe.recv()  # we wait for response to block the ui
        pipe.close()
        tk.terminate()

        logger.info('Changed "' + config_key + '" to ' + new_dir)
        return is_new_dir

    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        logger.info('Change save directory')
        self.ask_directory('save_directory')

    @rumps.clicked('Change WeChat directory')
    def set_wechat_dir(self, _):
        logger.info('Change WeChat directory')
        is_new_dir = self.ask_directory('wechat_directory')
        if is_new_dir:
            self.wechat_watcher_thread.restart_watcher()

    @rumps.clicked('Toggle icon')
    def toggle_icon(self, _):
        self.icon = None if self.icon else self._default_icon
        self.title = None

    @rumps.clicked('Reset preferences')
    def reset_preferences(self, _):
        logger.info('Reset preferences')
        tk, pipe = self.get_tk_process()
        pipe.send(('askokcancel', 'Are you sure you want to reset your preferences?'))
        res = pipe.recv()
        if not res:
            logger.info('Reset preferences cancelled')
            return
        shutil.copy('.default_config.json', 'config.json')
        self.config = load_config()
        pipe.send(('showinfo', 'Preferences successfully reset!'))
        pipe.recv()  # we wait for response to block the ui
        pipe.close()
        tk.terminate()
        logger.info('Reset preferences success')
        self.wechat_watcher_thread.restart_watcher()

    @rumps.clicked('Quit')
    def safe_quit(self, _):
        logger.info('Quit')
        self.wechat_watcher_thread.stop()
        rumps.quit_application()
