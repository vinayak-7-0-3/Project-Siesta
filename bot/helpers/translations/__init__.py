from bot.settings import bot_set
from .tr_en import EN
from .tr_hi import HI

lang = None
if bot_set.bot_lang == "hi":
    lang = HI()
else:
    lang = EN()