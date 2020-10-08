import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging

logger = logging.getLogger(__name__)


# def get_filename_pieces(filename):
#     try:
#         extension_index = filename.rindex('.')
#     except ValueError:
#         return (filename, '', '')
#
#     extension = filename[extension_index:]
#
#     try:
#         second_dot_index = filename.rindex('.', 0, extension_index)
#     except ValueError:
#         file = filename[:extension_index]
#         return (file, '', extension)
#
#     subextension = filename[second_dot_index: extension_index]
#     file = filename[:second_dot_index]
#     return (file, subextension, extension)

def get_on_moved(self):
    def on_moved(event):
        logger.info('On Moved:', Path(event.src_path).name + ' -> ' + Path(event.dest_path).name)
        path = Path(event.dest_path)
        if not self.filter(path):
            logger.info('Moved: ' + path.name + ' filtered')
            return

        save_dir = Path(self.save_directory)

        try:

            filename = path.name
            try:
                shutil.copyfile(path, save_dir / filename)
            except IOError as io_error:
                # if save_dir has not been made yet
                save_dir.mkdir()
                shutil.copyfile(path, save_dir / filename)
            logger.info('Saved:', Path(event.src_path).name)
        except Exception as e:
            logger.info('on_created Error:')
            logger.info(e)

    return on_moved


def get_on_created(self):
    def on_created(event):
        logger.info('On Created:', event.src_path)
        try:
            save_dir = Path(self.save_directory)
            path = Path(event.src_path)
            filename = path.name

            if not self.filter(filename):
                return

            try:
                shutil.copyfile(path, save_dir / filename)
            except IOError as io_error:
                # if save_dir has not been made yet
                save_dir.mkdir()
                shutil.copyfile(path, save_dir / filename)

            logger.info('Saved:', Path(event.src_path).name)
        except Exception as e:
            logger.info('on_created Error:')
            logger.info(e)

    return on_created


class DirectoryWatcher:
    def __init__(self, watch_directory, save_directory, filter=lambda x: True):
        self.watch_directory = watch_directory
        self.save_directory = save_directory
        self.filter = filter
        self._observer = None

    def restart(self, watch_directory, save_directory=None, filter=None):
        self.watch_directory = watch_directory
        self.save_directory = self.save_directory or save_directory
        self.filter = self.filter or filter
        self.stop()
        self.run()

    def run(self):
        patterns = "*"
        ignore_patterns = ""
        ignore_directories = True
        case_sensitive = True
        handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        handler.on_created = get_on_created(self)
        handler.on_moved = get_on_moved(self)

        # Create observer
        self._observer = Observer()
        self._observer.schedule(handler, self.watch_directory, recursive=True)
        self._observer.start()

        logger.info('Watching: ' + self.watch_directory)

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer = None