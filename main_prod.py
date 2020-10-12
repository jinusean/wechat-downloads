

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    os.environ["PY_ENV"] = "production"

    print('----------------------------------')
    print('Running in {} mode'.format(os.getenv('PY_ENV')))
    print('----------------------------------')

    from pathlib import Path
    from logging.handlers import RotatingFileHandler
    import logging
    import sys, traceback
    from lib import mac_dialogs

    # Ensure logs directory exists
    logs_filepath = os.getenv('LOGGING_FILEPATH')
    if '~' in logs_filepath:
        logs_filepath = logs_filepath.replace('~', str(Path.home()))
    logs_filepath = Path(logs_filepath)
    logs_filepath.parent.mkdir(exist_ok=True, parents=True)

    max_bytes = 10 * 1024 * 1024  # 10MB
    rh = RotatingFileHandler(logs_filepath, maxBytes=max_bytes, backupCount=5)
    sh = logging.StreamHandler()

    logging.basicConfig(
        handlers=[rh, sh],
        format=os.getenv('LOGGING_FORMAT'),
        datefmt=os.getenv("LOGGING_DATEFMT"),
        level=getattr(logging, os.getenv("LOGGING_LEVEL"))
    )


    # save unhandled exceptions to log file
    def handle_uncaught_exceptions(exctype, value, tb):
        exception_string = ''.join(traceback.format_list(traceback.extract_tb(tb)))
        logging.error(exception_string)
        mac_dialogs.confirm(message='Application encountered a fatal error\nContact the developer',
                            title='WeChat Downloads Fatal Error')
        excepthook(exctype, value, tb)


    excepthook = sys.excepthook
    sys.excepthook = handle_uncaught_exceptions

    from src.WeChatDownloadsApp import WeChatDownloadsApp

    app = WeChatDownloadsApp(name=os.getenv('APP_NAME'), settings=os.getenv('SETTINGS_FILENAME'))
    logging.info('Running in {} mode'.format(os.getenv('PY_ENV')))
    app.run()
