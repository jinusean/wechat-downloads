import logging.config
import os
import logging
from datetime import datetime

if __name__ == '__main__':
    logging_config = 'development'
    logging_config = 'logging_config/{}.ini'.format(logging_config)
    print('LOGGING:', logging_config)
    logging.config.fileConfig(fname=logging_config)

    # imports must come after logging is configurated
    from src.WatchWeChatDownloadsApp import WatchWeChatDownloads
    app = WatchWeChatDownloads('JamesLee')
    app.run()




