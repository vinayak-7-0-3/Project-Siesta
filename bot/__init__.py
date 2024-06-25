from config import Config
from pyrogram import Client

bot = Config.BOT_USERNAME

plugins = dict(
    root="bot/modules"
)

class CMD(object):
    START = ["start", f"start@{bot}"]
    HELP = ["help", f"help@{bot}"]
    SETTINGS = ["settings", f"settings@{bot}"]
    DOWNLOAD = ["download", f"download@{bot}"]
    BAN = ["ban", f"ban@{bot}"]
    AUTH = ["auth", f"auth@{bot}"]

aio = Client(
    "Project-Siesta",
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN,
    plugins=plugins,
    workdir=Config.WORK_DIR,
    workers=100
)

cmd = CMD()