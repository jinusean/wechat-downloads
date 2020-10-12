from pathlib import Path
from watchers.UserWatcher import UserWatcher
from lib.watchers import DirectoryWatcher
import logging
from abc import abstractmethod


def logger(self):
    return logging.getLogger(self.__class__.__name__)


def build_watcher(*args, **kwargs):
    watcher = DirectoryWatcher(*args, **kwargs)

    def watch_dir(self, path):
        raise NotImplemented('"watch_dir" needs to be implemented.')

    def on_created(self, event):
        self.watch_dir(event.src_path)

    def on_deleted(self, event):
        self.delete_watcher(event.src_path)

    def on_start(self):
        for path in Path(self.directory).iterdir():
            self.watch_dir(str(path))

        if len(self.watchers.keys()) == 0:
            logger(self).warning('No valid children directories found')

    watcher.on_created = on_created
    watcher.on_deleted = on_deleted
    watcher.on_start = on_start
    watcher.watch_dir = watch_dir

    return watcher


class _WeChatWatcher(DirectoryWatcher):
    @abstractmethod
    def watch_dir(self, path):
        pass

    def on_created(self, event):
        self.watch_dir(event.src_path)

    def on_deleted(self, event):
        self.delete_watcher(event.src_path)

    def on_start(self):
        for path in Path(self.directory).iterdir():
            self.watch_dir(str(path))

        if len(self.watchers.keys()) == 0:
            logger(self).warning('No valid children directories found')


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


