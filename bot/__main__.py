import os
import asyncio
import requests

from bot import Config

from .logger import LOGGER
from .tgclient import aio

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    aio.run()
    