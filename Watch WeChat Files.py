import time
from watch_wechat_files.WeChatWatcher import WeChatWatcher
from os.path import expanduser, join as join_path
import json
import rumps

from threading import Thread


def load_config():
    with open('config.json') as f:
        config = json.load(f)

    if config['is_initialized'] == False:
        home_path = expanduser('~')
        config['wechat_directory'] = join_path(home_path, config['wechat_directory'])
        config['save_directory'] = join_path(home_path, config['save_directory'])

    return config


def save_config(config):
    with open('config.json', 'wb') as f:
        json.dump(config, f)


class WatchWeChatDownloads(rumps.App):
    def __init__(self, name):
        super().__init__(name, icon='images/icon.icns')
        self.config = load_config()
        self.wechat_watcher = WeChatWatcher(self.config)

    def run(self):
        self.start_thread()
        super().run()

    def start_thread(self):
        def thread_fn():
            self.wechat_watcher.start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.wechat_watcher.stop()

        self.thread = Thread(target=thread_fn)
        self.thread.daemon = True
        self.thread.start()

    @rumps.clicked('Change save directory')
    def set_save_dir(self, _):
        print('set_save_dir')
        rumps.alert("jk! no preferences available!")
        # open dialog box and get new save_directory
        # self.config['save_directory'] = save_directory
        # save_config(self.config)

    @rumps.clicked('Change WeChat app location')
    def set_wechat_dir(self, _):
        print('set wechat dir')
        rumps.alert("jk! no preferences available!")
        # self.config['wechat_directory'] = wechat_directory
        # save_config(self.config)

    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.alert("jk! no preferences available!")


app = WatchWeChatDownloads('JamesLee')
app.run()