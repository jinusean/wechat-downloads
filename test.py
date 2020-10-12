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


# print(get_filename_pieces("13.pic_hd.dftemp.jpg"))

from  pathlib import Path
a = Path("/Users/suah/Datasets/Binance/binance.zip")
print(a.parent / ('hi' + 'asdf'))