from subprocess import Popen, PIPE

icon = 'Macintosh HD:Users:suah:PycharmProjects:WeChatDownloads:images:icon.icns'


def _decode_dirpath(binary):
    return binary.decode('utf-8').replace('alias Macintosh HD', '').replace(':', '/').strip()


def _decode_button(binary):
    return binary.decode('utf-8').replace('button returned:', '').strip()


def _execute(cmd):
    proc = Popen(["osascript", '-'], stdin=PIPE, stdout=PIPE)
    res, _ = proc.communicate(cmd)
    return res


def confirm(message, title="", default_button="Ok"):
    cmd = f"""
            display dialog "{message}" with icon file "{icon}" with title "{title}"\
            buttons {{"{default_button}"}} default button "{default_button}"
            """.encode()

    return _decode_button(_execute(cmd)) == default_button


def dialog(message, title="", default_button='Ok', cancel_button='Cancel'):
    cmd = f"""
            display dialog "{message}" with icon file "{icon}" with title "{title}"\
            buttons {{"{cancel_button}", "{default_button}"}} default button "{default_button}" cancel button "{cancel_button}"
            """.encode()

    return _decode_button(_execute(cmd)) == default_button


def alert(title, message, default_button='Ok', cancel_button='Cancel', type='informational'):
    assert type in ['critical', 'informational', 'warning']
    cmd = f"""
            display alert "{title}" message "{message}" as {type}\
            buttons {{"{cancel_button}", "{default_button}"}} default button "{default_button}" cancel button "{cancel_button}"
            """.encode()
    # with icon alias iconFile
    return _decode_button(_execute(cmd)) == default_button


def directory(directory, message=''):
    cmd = f"""
            set strPath to "{directory}"         
            set outputFolder to choose folder with prompt "{message}" default location strPath
            """.encode()
    return _decode_dirpath(_execute(cmd))
