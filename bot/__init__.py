from config import Config

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
    LOG = ["log", f"log@{bot}"]
    SETVAR = ['setvar', f'setvar@{bot}']

cmd = CMD()