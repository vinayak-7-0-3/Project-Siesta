from bot import CMD
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from ..settings import bot_set
from ..helpers.translations import lang
from ..helpers.buttons.settings import *
from ..helpers.database.pg_impl import set_db
from ..helpers.message import send_message, edit_message, check_user, fetch_user_details

@Client.on_message(filters.command(CMD.SETTINGS))
async def settings(c, message):
    if await check_user(message.from_user.id, restricted=True):
        user = await fetch_user_details(message)
        await send_message(user, lang.INIT_SETTINGS_PANEL, markup=main_menu())



#--------------------

# TELEGRAM SETTINGS

#--------------------
@Client.on_callback_query(filters.regex(pattern=r"^tgPanel"))
async def tg_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message, 
            lang.TELEGRAM_PANEL.format(
                bot_set.bot_public,
                bot_set.bot_lang,
                len(bot_set.admins),
                len(bot_set.auth_users),
                len(bot_set.auth_chats),
                bot_set.upload_mode
            ),
            markup=tg_button(bot_set.bot_public, bot_set.anti_spam, bot_set.alb_art, bot_set.upload_mode)
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

@Client.on_callback_query(filters.regex(pattern=r"^upload"))
async def upload_mode_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        modes = ['Local', 'Telegram']
        modes_count = 2
        if bot_set.rclone:
            modes.append('RCLONE')
            modes_count+=1

        current = modes.index(bot_set.upload_mode)
        nexti = (current + 1) % modes_count
        bot_set.upload_mode = modes[nexti]
        set_db.set_variable('UPLOAD_MODE', modes[nexti])
        try:
            await tg_cb(client, cb)
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^albArt"))
async def alb_art_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        alb_art = bot_set.alb_art
        alb_art = False if alb_art else True
        bot_set.alb_art = alb_art
        set_db.set_variable('ALBUM_ART_POST', alb_art)
        await tg_cb(client, cb)

#--------------------

# QOBUZ

#--------------------

@Client.on_callback_query(filters.regex(pattern=r"^qbP"))
async def qobuz_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        quality = {5:'MP3 320', 6:'Lossless', 7:'24B<=96KHZ',27:'24B>96KHZ'}
        current = bot_set.qobuz.quality
        quality[current] = quality[current] + '✅'
        try:
            await edit_message(
                cb.message,
                lang.QOBUZ_QUALITY_PANEL,
                markup=qb_button(quality)
            )
        except:pass

@Client.on_callback_query(filters.regex(pattern=r"^qbQ"))
async def qobuz_quality_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        qobuz = {5:'MP3 320', 6:'Lossless', 7:'24B<=96KHZ',27:'24B>96KHZ'}
        to_set = cb.data.split('_')[1]
        bot_set.qobuz.quality = list(filter(lambda x: qobuz[x] == to_set, qobuz))[0]
        await qobuz_cb(c, cb)



#--------------------

# COMMON

#--------------------
@Client.on_callback_query(filters.regex(pattern=r"^main_menu"))
async def main_menu_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        try:
            await edit_message(cb.message, lang.INIT_SETTINGS_PANEL, markup=main_menu())
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^close"))
async def close_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        try:
            await client.delete_messages(
                chat_id=cb.message.chat.id,
                message_ids=cb.message.id
            )
        except:
            pass

@Client.on_message(filters.command(CMD.BAN))
async def ban(client:Client, msg:Message):
    if await check_user(msg.from_user.id, restricted=True):
        try:
            id = int(msg.text.split(" ", maxsplit=1)[1])
        except:
            await send_message(msg, lang.BAN_AUTH_FORMAT)
            return

        user = False if str(id).startswith('-100') else True
        if user:
            if id in bot_set.auth_users:
                bot_set.auth_users.remove(id)
                set_db.set_variable('AUTH_USERS', str(bot_set.auth_users))
            else: await send_message(msg, lang.USER_DOEST_EXIST)
        else:
            if id in bot_set.auth_chats:
                bot_set.auth_chats.remove(id)
                set_db.set_variable('AUTH_CHATS', str(bot_set.auth_chats))
            else: await send_message(msg, lang.USER_DOEST_EXIST)
        await send_message(msg, lang.BAN_ID)
        

@Client.on_message(filters.command(CMD.AUTH))
async def auth(client:Client, msg:Message):
    if await check_user(msg.from_user.id, restricted=True):
        try:
            id = int(msg.text.split(" ", maxsplit=1)[1])
        except:
            await send_message(msg, lang.BAN_AUTH_FORMAT)
            return

        user = False if str(id).startswith('-100') else True
        if user:
            if id not in bot_set.auth_users:
                bot_set.auth_users.append(id)
                set_db.set_variable('AUTH_USERS', str(bot_set.auth_users))
            else: await send_message(msg, lang.USER_EXIST)
        else:
            if id not in bot_set.auth_chats:
                bot_set.auth_chats.append(id)
                set_db.set_variable('AUTH_CHATS', str(bot_set.auth_chats))
            else: await send_message(msg, lang.USER_EXIST)
        await send_message(msg, lang.AUTH_ID)