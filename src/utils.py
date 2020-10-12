from pathlib import Path
from src.Settings import Settings
from src.managers import WatchersManager
from lib import mac_dialogs
import shutil
import rumps


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


def copy_file(src):
    src = Path(src)
    save_dir = Settings()['save_directory']
    save_dir = Path(save_dir)
    try:
        shutil.copyfile(src, save_dir / src.name)
    except IOError as io_error:
        # if save_dir has not been made yet
        save_dir.mkdir()
        shutil.copyfile(src, save_dir / src.name)


def validate_file(filepath):
    path = Path(filepath)
    filename = path.name

    if not path.is_file() or filename in Settings()['exclude_files']:
        return False

    file, subextension, extension = get_filename_pieces(filename)

    for invalid_subextension in Settings()['exclude_subextensions']:
        if invalid_subextension in subextension:
            return False

    if subextension == '.pic' and (path.parent / (file + '.pic_hd' + extension)).exists():
        # '.pic' also usually have '.pic_hd'
        return False

    return True

def validate_file_and_copy(filepath):
    if validate_file(filepath):
        copy_file(filepath)
        return True
    return False





def iter_files(path):
    path = Path(path)
    for file in path.glob('**/*'):
        if file.is_file():
            yield file


def sync_files(start_time, end_time):

    count = 0
    for file in iter_user_files():
        stat = file.stat()
        modified_time = stat.st_mtime
        if start_time > modified_time or modified_time > end_time:
            # if last synced happened after file modification
            # if app has started before file modification
            continue
        copy_file(file)
        count += 1
    print("Synced {} files".format(count))
    rumps.notification(message="Synced {} files".format(count), title="WeChat Downloads", subtitle='Autosync')



def iter_user_files():
    manager = WatchersManager()
    for dir in manager.get_dirs_by_cls('UserWatcher'):
        for file in iter_files(dir):
            if validate_file(file):
                yield file

def sync_all():
    count = 0
    for file in iter_files():
        copy_file(file)
        count += 1

    if count == 0:
        message = 'No files to copy...'
    else:
        message = 'Copied {} files to:\n{}!'.format(count, Settings()['save_directory'])
    rumps.notification(message=message, title="WeChat Downloads", subtitle='Sync all files')