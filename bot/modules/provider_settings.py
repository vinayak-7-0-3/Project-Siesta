import bot.helpers.translations as lang

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from ..settings import bot_set
from ..helpers.buttons.settings import *
from ..helpers.database.pg_impl import set_db
from ..helpers.message import edit_message, check_user




@Client.on_callback_query(filters.regex(pattern=r"^providerPanel"))
async def provider_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message,
            lang.s.PROVIDERS_PANEL,
            providers_button()
        )



@Client.on_callback_query(filters.regex(pattern=r"^qbP"))
async def qobuz_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        quality = {5:'MP3 320', 6:'Lossless', 7:'24B<=96KHZ',27:'24B>96KHZ'}
        current = bot_set.qobuz.quality
        quality[current] = quality[current] + '✅'
        try:
            await edit_message(
                cb.message,
                lang.s.QOBUZ_QUALITY_PANEL,
                markup=qb_button(quality)
            )
        except:pass



@Client.on_callback_query(filters.regex(pattern=r"^qbQ"))
async def qobuz_quality_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        qobuz = {5:'MP3 320', 6:'Lossless', 7:'24B<=96KHZ',27:'24B>96KHZ'}
        to_set = cb.data.split('_')[1]
        bot_set.qobuz.quality = list(filter(lambda x: qobuz[x] == to_set, qobuz))[0]
        set_db.set_variable('QOBUZ_QUALITY', bot_set.qobuz.quality)
        await qobuz_cb(c, cb)