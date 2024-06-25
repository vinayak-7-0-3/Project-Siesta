import os
import asyncio
import requests

from pyrogram import idle
from bot import aio, Config
from .logger import LOGGER
from .helpers.settings import bot_set

async def start():
    pass

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    
    loop = asyncio.new_event_loop()
    future = loop.run_until_complete(start())
    aio.start()
    LOGGER.info("BOT : Started Successfully")
    idle()
    aio.stop()
    if os.path.exists('rclone.conf'):
        os.remove('rclone.conf')
    LOGGER.info('BOT : Exited Successfully ! Bye..........')