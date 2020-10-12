from pathlib import Path
from src.Settings import Settings
import shutil


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
