from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from src.DownloadsWatcher import DownloadsWatcher
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WeChatWatcher:
    def __init__(self, config):
        self.config = config
        self.wechat_observer = None
        self.messages_watcher = DownloadsWatcher(config)

    def stop(self):
        if self.wechat_observer:
            self.wechat_observer.stop()
            self.wechat_observer.join()
            self.wechat_observer = None
        self.messages_watcher.stop()

    def start(self):
        self.stop()
        wechat_directory = self.config["wechat_directory"]


        def get_on_event(mode):
            def on_event(event):
                path = Path(event.src_path)
                if not path.is_dir():
                    logger.info(str(path) + ' created (non-directories are ignored)')
                    return
                logger.info('Restarting:', event.src_path, mode)
                self.start()

            return on_event

        # Create handler
        patterns = "*"
        ignore_patterns = ""
        ignore_directories = False
        case_sensitive = True
        wechat_dir_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        wechat_dir_handler.on_created = get_on_event('created')
        wechat_dir_handler.on_modified = get_on_event('modified')

        # Create observer
        wechat_observer = Observer()
        wechat_observer.schedule(wechat_dir_handler, wechat_directory, recursive=False)

        wechat_observer.start()
        logger.info('Starting: ' + wechat_directory)
        self.messages_watcher.start()
