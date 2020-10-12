from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from src.Settings import Settings
import shutil
import logging
from pathlib import Path

logger = logging.getLogger('UserWatcher')


def get_filename_pieces(filename):
    try:
        extension_index = filename.rindex('.')
    except ValueError:
        return (filename, '', '')

    extension = filename[extension_index:]

    try:
        second_dot_index = filename.rindex('.', 0, extension_index)
    except ValueError:
        file = filename[:extension_index]
        return (file, '', extension)

    subextension = filename[second_dot_index: extension_index]
    file = filename[:second_dot_index]
    return (file, subextension, extension)


class UserWatcher:
    def __init__(self, directory):
        self.directory = directory  # user directory
        self.watching_dir = None
        self.observer = None

    def on_moved(self, event):
        logger.info('Moved {} -> {}'.format(Path(event.src_path).name, Path(event.dest_path).name))
        save_dir = Path(Settings()['save_directory'])
        path = Path(event.dest_path)
        filename = path.name
        try:
            shutil.copyfile(path, save_dir / filename)
        except IOError as io_error:
            # if save_dir has not been made yet
            save_dir.mkdir()
            shutil.copyfile(path, save_dir / filename)
        logger.info('SAVED: {} -> {}'.format(Path(event.src_path).name, Path(event.dest_path).name))

    def on_created(self, event):
        path = Path(event.src_path)
        logger.info('Created: {}'.format(path.name))
        settings = Settings()
        save_dir = Path(settings['save_directory'])
        filename = path.name

        if not path.is_file() or filename in settings['exclude_files']:
            return

        file, subextension, extension = get_filename_pieces(filename)

        for invalid_subextension in settings['exclude_subextensions']:
            if invalid_subextension in subextension:
                return


        if subextension == '.pic' and (path.parent / (file + '.pic_hd' + extension)).exists():
            # '.pic' also usually have '.pic_hd'
            return

        try:
            shutil.copyfile(path, save_dir / filename)
        except IOError as io_error:
            # if save_dir has not been made yet
            save_dir.mkdir()
            shutil.copyfile(path, save_dir / filename)

        logger.info('SAVED: ' + filename)

    def stop(self):
        logger.info('Stopped: ' + self.directory)
        self.observer.stop()
        self.observer = None
        self.watching_dir = None

    def start(self):
        message_temp_dir = Path(self.directory) / 'Message/MessageTemp'
        message_temp_dir.mkdir(exist_ok=True)
        message_temp_dir = str(message_temp_dir)
        logger.info('Watching: ' + message_temp_dir)

        handler = PatternMatchingEventHandler(
            patterns="*",
            ignore_patterns="",
            ignore_directories=True,
            case_sensitive=True)

        handler.on_created = self.on_created
        handler.on_moved = self.on_moved
        handler.on_deleted = lambda event: print('Deleted: {}'.format(event.src_path))

        # Create observer
        observer = Observer()
        observer.schedule(handler, message_temp_dir, recursive=True)
        observer.start()

        self.observer = observer
        self.watching_dir = message_temp_dir
