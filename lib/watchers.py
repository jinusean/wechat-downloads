from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging

def logger(self):
    return logging.getLogger(self.__class__.__name__)

class DirectoryWatcher:
    # overrideable methods
    on_created = None
    on_modified = None
    on_deleted = None
    on_moved = None

    def on_start(self):
        pass

    def __init__(self, directory,
                 patterns='*',
                 ignore_patterns='',
                 ignore_directories=False,
                 case_sensitive=True,
                 recursive=False):
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

    def start(self):
        # Create handler
        handler = PatternMatchingEventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=self.ignore_directories,
            case_sensitive=self.case_sensitive)

        for event_method in ['on_created', 'on_deleted', 'on_modified', 'on_moved']:
            if hasattr(self, event_method):
                setattr(handler, event_method, getattr(self, event_method))

        # Create observer
        observer = Observer()
        observer.schedule(handler, self.directory, recursive=self.recursive)
        observer.start()
        self.observer = observer

        logger(self).info('Watching: ' + self.directory)

        self.on_start()
