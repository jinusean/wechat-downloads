import logging
from threading import Thread, Event
from .WeChatWatcher import WeChatWatcher

logger = logging.getLogger(__name__)

class WeChatWatcherThread(Thread):
    def __init__(self, config, queue):
        super().__init__()
        self.config = config
        self.queue = queue
        self.wechat_watcher = WeChatWatcher(config)
        self.stop_event = Event()

    def restart_watcher(self):
        # used when WeChat directory has changed
        self.wechat_watcher.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        logger.info('starting')
        try:
            self.wechat_watcher.start()
            while not self.stop_event.wait(10):
                continue
            self.wechat_watcher.stop()
            logger.info('stopped')
        except Exception as e:
            print('Thread error')
            print(e)
