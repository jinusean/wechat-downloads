import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


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


def get_on_created(config):
    def on_created(event):
        try:
            save_dir = Path(config['save_directory'])
            path = Path(event.src_path)

            print('Received', path.name)

            if not path.is_file():
                return

            filename = path.name
            if filename in config['ignore_list']:
                return

            file, subextension, extension = get_filename_pieces(filename)

            if '_thumb' in subextension or '_hd' in subextension or '_tmp' in subextension:
                # ignore thumb files and HD files
                return

            if subextension == '.pic':
                hd_filename = file + '.pic_hd' + extension
                hd_filepath = path.absolute().parent / hd_filename
                if hd_filepath.exists():
                    path = hd_filepath

            try:
                shutil.copyfile(path, save_dir / filename)
            except IOError as io_error:
                save_dir.mkdir()
                shutil.copyfile(path, save_dir / filename)

            print('Saved ' + filename + ' to ' + str(save_dir))
        except Exception as e:
            print('on_created Error:')
            print(e)

    return on_created


class MessagesWatcher:
    def __init__(self, config):
        self.observers = []
        self.config = config

    def stop(self):
        for observer in self.observers:
            observer.stop()
        self.observers = []

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

        for dirpath in self.find_message_temp_dirs(latest_version_directory):
            # Create handler
            patterns = "*"
            ignore_patterns = ""
            ignore_directories = False
            case_sensitive = True
            my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories,
                                                           case_sensitive)
            my_event_handler.on_created = get_on_created(self.config)

            # Create observer
            observer = Observer()
            observer.schedule(my_event_handler, str(dirpath), recursive=True)
            observer.start()

            print('- watching:', str(dirpath)[len(str(latest_version_directory)):])
            self.observers.append(observer)

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
