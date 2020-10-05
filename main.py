import logging.config
import logging



if __name__ == '__main__':
    logging_config = 'logging_config/development.ini'

    logging.config.fileConfig(fname=logging_config)

    # imports must come after logging is configured
    from src.WeChatDownloadsApp import WeChatDownloadsApp
    app = WeChatDownloadsApp()

    app.run()
