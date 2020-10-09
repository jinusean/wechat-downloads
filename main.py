import os
from dotenv import load_dotenv

load_dotenv()


def produce():
    from logging.handlers import RotatingFileHandler

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

def develop():
    import logging.config
    import atexit
    import shutil
    import rumps

    logging_config = 'configs/logging_dev.ini'
    logging.config.fileConfig(fname=logging_config)


    ### cleanup before exit
    quit_application = rumps.quit_application

    def dev_exit_handler(*args, **kwargs):
        application_support_dir = Path(Path.home(), 'Library/Application Support', os.getenv('APP_NAME'))
        try:
            print('Cleanup: deleting /Application Support: ' + str(application_support_dir))
            shutil.rmtree(application_support_dir)
        except Exception:
            pass
        finally:
            quit_application(*args, **kwargs)

    atexit.register(dev_exit_handler)
    rumps.quit_application = dev_exit_handler


if __name__ == '__main__':
    import logging
    from pathlib import Path

    if os.environ.get('PY_ENV') == 'production':
        produce()
    else:
        develop()



    #### start app
    # import app after logging is configured first
    from src.WeChatDownloadsApp import WeChatDownloadsApp

    app = WeChatDownloadsApp(os.getenv('APP_NAME'))
    app.run()











