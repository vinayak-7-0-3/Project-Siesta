import bot.helpers.translations as lang

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from ..settings import bot_set
from ..helpers.translations import lang_available
from ..helpers.buttons.settings import *
from ..helpers.database.pg_impl import set_db
from ..helpers.message import edit_message, check_user



@Client.on_callback_query(filters.regex(pattern=r"^tgPanel"))
async def tg_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message, 
            lang.s.TELEGRAM_PANEL.format(
                bot_set.bot_public,
                bot_set.bot_lang,
                len(bot_set.admins),
                len(bot_set.auth_users),
                len(bot_set.auth_chats),
                bot_set.upload_mode
            ),
            markup=tg_button()
        )


@Client.on_callback_query(filters.regex(pattern=r"^botPublic"))
async def bot_public_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        bot_set.bot_public = False if bot_set.bot_public else True
        set_db.set_variable('BOT_PUBLIC', bot_set.bot_public)
        try:
            await tg_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^antiSpam"))
async def anti_spam_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        anti = ['OFF', 'USER', 'CHAT+']
        current = anti.index(bot_set.anti_spam)
        nexti = (current + 1) % 3
        bot_set.anti_spam = anti[nexti]
        set_db.set_variable('ANTI_SPAM', anti[nexti])
        try:
            await tg_cb(client, cb)
        except:
            pass



@Client.on_callback_query(filters.regex(pattern=r"^langPanel"))
async def language_panel_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        current = bot_set.bot_lang
        await edit_message(
            cb.message,
            lang.s.LANGUAGE_PANEL,
            language_buttons(lang_available, current)
        )



@Client.on_callback_query(filters.regex(pattern=r"^langSet"))
async def set_language_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        to_set = cb.data.split('_')[1]
        bot_set.bot_lang = to_set
        set_db.set_variable('BOT_LANGUAGE', to_set)
        bot_set.set_language()
        try:
            await language_panel_cb(client, cb)
        except:
            pass


