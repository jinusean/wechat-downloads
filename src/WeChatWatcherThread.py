import logging
from threading import Thread, Event
from .WeChatWatcher import WeChatWatcher

logger = logging.getLogger(__name__)

class WeChatWatcherThread(Thread):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.wechat_watcher = WeChatWatcher(config)
        self.stop_event = Event()

    def restart_watcher(self):
        self.wechat_watcher.stop()
        self.wechat_watcher.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        logger.info('starting')
        self.wechat_watcher.start()
        while not self.stop_event.wait(1):
            continue
        self.wechat_watcher.stop()
        logger.info('stopped')