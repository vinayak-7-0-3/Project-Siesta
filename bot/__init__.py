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

cmd = CMD()