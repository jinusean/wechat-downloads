from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from .MessagesWatcher import MessagesWatcher


class WeChatWatcher:
    def __init__(self, config):
        self.config = config
        self.wechat_observer = None
        self.messages_watcher = MessagesWatcher(config)

    def stop(self):
        if self.wechat_observer:
            self.wechat_observer.stop()
            self.wechat_observer = None
        self.messages_watcher.stop()

    def start(self):
        wechat_directory = self.config["wechat_directory"]
        self.stop()

        def on_new_wechat_version_directory(event):
            print('New WeChat version directory created:', event.src_path)
            self.start()

        # Create handler
        patterns = "*"
        ignore_patterns = ""
        ignore_directories = False
        case_sensitive = True
        wechat_dir_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        wechat_dir_handler.on_created = on_new_wechat_version_directory

        # Create observer
        wechat_observer = Observer()
        wechat_observer.schedule(wechat_dir_handler, wechat_directory, recursive=False)
        wechat_observer.start()

        print('Starting: ' + wechat_directory)
        self.messages_watcher.start()
