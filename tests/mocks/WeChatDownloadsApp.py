import os

class WeChatDownloadsApp:
    def open(self, *args):
        return open(os.path.join('tests/mocks/', *args[0]), *args[1:])