from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
from pathlib import Path
from src.managers import WatchersManager
from src.utils import validate_file_and_copy, copy_file

logger = logging.getLogger('UserWatcher')



class UserWatcher:
    def __init__(self, directory):
        self.directory = directory  # user directory
        self.watching_dir = None
        self.observer = None

    def on_moved(self, event):
        logger.info('Moved {} -> {}'.format(Path(event.src_path).name, Path(event.dest_path).name))
        copy_file(event.dest_path)
        logger.info('SAVED: {} -> {}'.format(Path(event.src_path).name, Path(event.dest_path).name))

    def on_created(self, event):
        path = Path(event.src_path)
        filename = path.name
        logger.info('Created: {}'.format(filename))
        if validate_file_and_copy(event.src_path):
            logger.info('SAVED: ' + filename)

    def stop(self):
        self.observer.stop()
        self.observer = None
        WatchersManager().remove(self, self.watching_dir)
        self.watching_dir = None

    def start(self):
        message_temp_dir = Path(self.directory) / 'Message/MessageTemp'
        message_temp_dir.mkdir(exist_ok=True)
        message_temp_dir = str(message_temp_dir)

        handler = PatternMatchingEventHandler(
            patterns="*",
            ignore_patterns="",
            ignore_directories=True,
            case_sensitive=True)

        handler.on_created = self.on_created
        handler.on_moved = self.on_moved

        # Create observer
        observer = Observer()
        observer.schedule(handler, message_temp_dir, recursive=True)
        observer.start()

        self.observer = observer
        self.watching_dir = message_temp_dir
        WatchersManager().add(self, message_temp_dir)
