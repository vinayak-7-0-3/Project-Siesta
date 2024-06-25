import os
import logging
import inspect

from bot import aio

log_file_path = "./bot/bot_logs.log"

class Logger:

    def __init__(self):
        # Config file has logging so removing that handler 
        try:
            logging.getLogger().removeHandler(logging.getLogger().handlers[0])
        except:
            pass
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger("pyrogram").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
        logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
        logging.getLogger("Librespot:Session").setLevel(logging.WARNING)
        logging.getLogger("Librespot:MercuryClient").setLevel(logging.WARNING)
        logging.getLogger("Librespot:TokenProvider").setLevel(logging.WARNING)
        logging.getLogger("librespot.audio").setLevel(logging.WARNING)
        logging.getLogger("Librespot:ApiClient").setLevel(logging.WARNING)
        logging.getLogger("pydub").setLevel(logging.WARNING)
        logging.getLogger("spotipy").setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Create file handler
        file_handler = logging.FileHandler(log_file_path, 'a', 'utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        caller_frame = inspect.currentframe().f_back
        caller_filename = os.path.basename(caller_frame.f_globals['__file__'])
        self.logger.debug(f'{caller_filename} - {message}')

    # Debug itself with no info
    def info(self, message):
        self.logger.info(message)

    async def error(self, message, user=None):
        caller_frame = inspect.currentframe().f_back
        caller_filename = os.path.basename(caller_frame.f_globals['__file__'])
        self.logger.error(f'{caller_filename} - {message}')

LOGGER = Logger()