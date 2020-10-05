import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging

logger = logging.getLogger(__name__)

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


def on_moved(event):
    # image files are first 'created' as a temp file and then moved once it is downloaded
    logger.info('Moved', Path(event.src_path).name, Path(event.dest_path).name)
    a = event


def get_on_moved(config):
    def on_moved(event):
        logger.info('Moved', Path(event.src_path).name + ' -> ' + Path(event.dest_path).name)
        try:
            save_dir = Path(config['save_directory'])
            path = Path(event.dest_path)
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

def get_on_created(config):
    def on_created(event):
        logger.info('Created:', event.src_path)
        try:
            save_dir = Path(config['save_directory'])
            path = Path(event.src_path)
            filename = path.name

            if not path.is_file() or filename in config['ignore_list']:
                return

            file, subextension, extension = get_filename_pieces(filename)

            for invalid_subextension in config['invalid_subextensions']:
                if invalid_subextension in subextension:
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


class DownloadsWatcher:
    def __init__(self, config):
        self.observers = []
        self.config = config
        self._directory = None
        self._watching_dirs =[]

    def stop(self):
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers = []

        self._directory = None
        self._watching_dirs = []

    def find_latest_version_directory(self):
        last_modified = 0
        latest_dir = None

        for dirpath in Path(self.config['wechat_directory']).iterdir():
            if not dirpath.is_dir():
                continue

            modified_time = dirpath.stat().st_mtime

            if modified_time > last_modified:
                last_modified = modified_time
                latest_dir = dirpath

        return latest_dir

    def start(self):
        latest_version_directory = self.find_latest_version_directory()

        message_temps = self.find_message_temp_dirs(latest_version_directory)
        if len(message_temps) == 0:
            logger.info('No message temps found...')

        for dirpath in message_temps:
            # Create handler
            patterns = "*"
            ignore_patterns = ""
            ignore_directories = True
            case_sensitive = True
            my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories,
                                                           case_sensitive)
            my_event_handler.on_created = get_on_created(self.config)
            my_event_handler.on_moved = get_on_moved(self.config)

            # Create observer
            observer = Observer()
            observer.schedule(my_event_handler, str(dirpath), recursive=True)
            observer.start()

            logger.info('Watching: ' + str(dirpath)[len(str(latest_version_directory)):], )
            self.observers.append(observer)
            self._watching_dirs.append(str(dirpath))

        self._directory = latest_version_directory

    def find_message_temp_dirs(self, path):
        paths = []
        for dirpath in Path(path).iterdir():
            if dirpath.name == 'Message':
                dirpath = dirpath / 'MessageTemp'
                dirpath.mkdir(exist_ok=True)
                paths.append(dirpath)
                continue
            if dirpath.is_dir():
                paths = paths + self.find_message_temp_dirs(dirpath)
        return paths
