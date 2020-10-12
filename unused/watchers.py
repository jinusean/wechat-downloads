from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
from watchers.UserWatcher import UserWatcher


def logger(self):
    return logging.getLogger(self.__class__.__name__)


class DirectoryWatcher:
    def __init__(self, directory,
                 patterns='*',
                 ignore_patterns='',
                 ignore_directories=False,
                 case_sensitive=True,
                 recursive=False):
        self.directory_watcher_class = None
        self.directory = directory
        self.observer = None
        self.watchers = {}
        self.patterns = patterns
        self.ignore_patterns = ignore_patterns
        self.ignore_directories = ignore_directories
        self.case_sensitive = case_sensitive
        self.recursive = recursive

    def delete_watcher(self, path):
        if path not in self.watchers:
            return

        watcher = self.watchers[path]
        watcher.stop()
        del self.watchers[path]

    def stop(self):
        logger(self).info('Stopped: ' + self.directory)
        for watcher in self.watchers.values():
            watcher.stop()
        self.watchers = {}

        self.observer.stop()
        self.observer = None

    def directory_filter(self, path):
        return True

    def watch_dir(self, path):
        if not self.directory_watcher_class \
                or not Path(path).is_dir() \
                or path in self.watchers \
                or not self.directory_filter(path):
            return
        watcher = self.directory_watcher_class(path)
        watcher.start()
        self.watchers[path] = watcher

    def on_created(self, event):
        self.watch_dir(event.src_path)

    def on_deleted(self, event):
        self.delete_watcher(event.src_path)

    def start(self):
        # Create handler
        handler = PatternMatchingEventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=self.ignore_directories,
            case_sensitive=self.case_sensitive)

        handler.on_created = self.on_created
        handler.on_deleted = self.on_deleted

        # Create observer
        observer = Observer()
        observer.schedule(handler, self.directory, recursive=self.recursive)
        observer.start()
        self.observer = observer

        logger(self).info('Watching: ' + self.directory)

        for path in Path(self.directory).iterdir():
            self.watch_dir(str(path))

        if len(self.watchers.keys()) == 0:
            logger(self).warning('No valid children directories found')


class VersionWatcher(DirectoryWatcher):
    _watcher_class = UserWatcher

    def watcher_filter(self, directory):
        # user directories are their guid of 32 length
        return len(Path(directory).name) == 32


class WeChatWatcher(DirectoryWatcher):
    """
    Watches WeChat directory for changes.
    Sets version watcher on changes
    """
    _watcher_class = VersionWatcher
