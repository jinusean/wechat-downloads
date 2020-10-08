from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from src.DownloadsWatcher import DownloadsWatcher
from src import ConfigManger
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WeChatWatcher:
    def __init__(self):
        self.wechat_observer = None
        self.downloads_watcher = DownloadsWatcher()


    def stop(self):
        if self.wechat_observer:
            self.wechat_observer.stop()
            self.wechat_observer.join()
            self.wechat_observer = None
        self.downloads_watcher.stop()

    def start(self):
        self.stop()

        config = ConfigManger.config()

        def get_on_event(mode):
            def on_event(event):
                path = Path(event.src_path)
                if not path.is_dir():
                    logger.info('{} {} (non-directories are ignored)'.format(str(path), mode))
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
        wechat_observer.schedule(wechat_dir_handler, config['wechat_directory'], recursive=False)

        wechat_observer.start()
        logger.info('Starting: ' + config['wechat_directory'])
        self.downloads_watcher.start()
