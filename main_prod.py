if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler
    from pathlib import Path
    from src.utils import load_config

    config = load_config()

    ##### setup logging
    # Ensure logs directory exists
    logs_directory = config['logging']['directory']
    if '~' in logs_directory:
        logs_directory = logs_directory.replace('~', str(Path.home()))
    logs_directory = Path(logs_directory)
    logs_directory.mkdir(exist_ok=True, parents=True)

    logs_path = logs_directory/'wechat_downloads.log'

    max_bytes = 10*1024*1024 # 10MB
    rh = RotatingFileHandler(logs_path, maxBytes=max_bytes, backupCount=5)
    sh = logging.StreamHandler()

    logging.basicConfig(
        handlers=[rh, sh],
        format=config['logging']['format'],
        datefmt=config['logging']['datefmt'],
        level=logging.INFO
    )


    #### start app
    # import app after logging is configured first
    from src.WeChatDownloadsApp import WeChatDownloadsApp
    app = WeChatDownloadsApp('JL')
    app.run()











