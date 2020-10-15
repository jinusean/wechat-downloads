if __name__ == '__main__':
    import os
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    # ----------------------- Setup logging
    import logging.config
    import rumps

    logging_config = 'configs/logging_dev.ini'
    logging.config.fileConfig(fname=logging_config)

    rumps.debug_mode(True)

    # ----------------------- Start app
    # import app after logging is configured first
    from src.WeChatDownloadsApp import WeChatDownloadsApp

    app = WeChatDownloadsApp(name=os.getenv('APP_NAME'), settings=os.getenv('SETTINGS_FILENAME'))

    app.run()

