from config import Config

from pyrogram import Client

from .logger import LOGGER
from .settings import bot_set

plugins = dict(
    root="bot/modules"
)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Project-Siesta",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.TG_BOT_TOKEN,
            plugins=plugins,
            workdir=Config.WORK_DIR,
            workers=100
        )

    async def start(self):
        await super().start()
        await bot_set.login_qobuz()
        await bot_set.login_deezer()
        LOGGER.info("BOT : Started Successfully")

    async def stop(self, *args):
        await super().stop()
        for client in bot_set.clients:
            await client.session.close()
        LOGGER.info('BOT : Exited Successfully ! Bye..........')

aio = Bot()