from pathlib import Path
from src.watchers.UserWatcher import UserWatcher
from lib.watchers import DirectoryWatcher
import logging
from abc import abstractmethod
from src.Manager import Manager


def logger(self):
    return logging.getLogger(self.__class__.__name__)


class _WeChatWatcher(DirectoryWatcher):
    @abstractmethod
    def watch_dir(self, path):
        pass

    def on_created(self, event):
        self.watch_dir(event.src_path)

    def on_deleted(self, event):
        self.delete_watcher(event.src_path)

    def on_start(self):
        Manager().add(self, self.directory)
        for path in Path(self.directory).iterdir():
            self.watch_dir(str(path))

        if len(self.watchers.keys()) == 0:
            logger(self).warning('No valid children directories found')

    def stop(self):
        Manager().remove(self, self.directory)
        super().stop()


class VersionWatcher(_WeChatWatcher):
    def watch_dir(self, path):
        if not Path(path).is_dir() or path in self.watchers or len(Path(path).name) != 32:
            return
        watcher = UserWatcher(path)
        watcher.start()
        self.watchers[path] = watcher


class WeChatWatcher(_WeChatWatcher):
    def watch_dir(self, path):
        if not Path(path).is_dir() or path in self.watchers:
            return
        watcher = VersionWatcher(path)
        watcher.start()
        self.watchers[path] = watcher
