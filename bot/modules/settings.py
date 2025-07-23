from bot import CMD
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

import bot.helpers.translations as lang

from ..settings import bot_set
from ..helpers.buttons.settings import *
from ..helpers.database.pg_impl import set_db
from ..helpers.message import send_message, edit_message, check_user, fetch_user_details

from config import DEEZER_VARS, TIDAL_VARS, QOBUZ_VARS, Config



@Client.on_message(filters.command(CMD.SETTINGS))
async def settings(c, message):
    if await check_user(message.from_user.id, restricted=True):
        user = await fetch_user_details(message)
        await send_message(user, lang.s.INIT_SETTINGS_PANEL, markup=main_menu())


@Client.on_callback_query(filters.regex(pattern=r"^corePanel"))
async def core_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message,
            lang.s.CORE_PANEL,
            core_buttons()
        )



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
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^linkOption"))
async def link_option_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        options = ['False', 'Index', 'RCLONE', 'Both']
        current = options.index(bot_set.link_options)
        nexti = (current + 1) % 4
        bot_set.link_options = options[nexti]
        set_db.set_variable('RCLONE_LINK_OPTIONS', options[nexti])
        try:
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^albArt"))
async def alb_art_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        art_post = bot_set.art_poster
        art_post = False if art_post else True
        bot_set.art_poster = art_post
        set_db.set_variable('ART_POSTER', art_post)
        try:
            await core_cb(client, cb)
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^playCONC"))
async def playlist_conc_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        play_conc = bot_set.playlist_conc
        play_conc = False if play_conc else True
        bot_set.playlist_conc = play_conc
        set_db.set_variable('PLAYLIST_CONCURRENT', play_conc)
        try:
            await core_cb(client, cb)
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^artBATCH"))
async def artist_conc_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        artist_batch = bot_set.artist_batch
        artist_batch = False if artist_batch else True
        bot_set.artist_batch = artist_batch
        set_db.set_variable('ARTIST_BATCH_UPLOAD', artist_batch)
        try:
            await core_cb(client, cb)
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^sortPlay"))
async def playlist_sort_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        sort = bot_set.playlist_sort
        sort = False if sort else True
        bot_set.playlist_sort = sort
        set_db.set_variable('PLAYLIST_SORT', sort)
        try:
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^playZip"))
async def playlist_zip_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        option = bot_set.playlist_zip
        option = False if option else True
        bot_set.playlist_zip = option
        set_db.set_variable('PLAYLIST_ZIP', option)
        try:
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^sortLinkPlay"))
async def playlist_disable_zip_link(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        option = bot_set.disable_sort_link
        option = False if option else True
        bot_set.disable_sort_link = option
        set_db.set_variable('PLAYLIST_LINK_DISABLE', option)
        try:
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^artZip"))
async def artist_zip_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        option = bot_set.artist_zip
        option = False if option else True
        bot_set.artist_zip = option
        set_db.set_variable('ARTIST_ZIP', option)
        try:
            await core_cb(client, cb)
        except:
            pass


@Client.on_callback_query(filters.regex(pattern=r"^albZip"))
async def album_zip_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        option = bot_set.album_zip
        option = False if option else True
        bot_set.album_zip = option
        set_db.set_variable('ALBUM_ZIP', option)
        try:
            await core_cb(client, cb)
        except:
            pass



#--------------------

# COMMON

#--------------------
@Client.on_callback_query(filters.regex(pattern=r"^main_menu"))
async def main_menu_cb(client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        try:
            await edit_message(cb.message, lang.s.INIT_SETTINGS_PANEL, markup=main_menu())
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
            await send_message(msg, lang.s.BAN_AUTH_FORMAT)
            return

        user = False if str(id).startswith('-100') else True
        if user:
            if id in bot_set.auth_users:
                bot_set.auth_users.remove(id)
                set_db.set_variable('AUTH_USERS', str(bot_set.auth_users))
            else: await send_message(msg, lang.s.USER_DOEST_EXIST)
        else:
            if id in bot_set.auth_chats:
                bot_set.auth_chats.remove(id)
                set_db.set_variable('AUTH_CHATS', str(bot_set.auth_chats))
            else: await send_message(msg, lang.s.USER_DOEST_EXIST)
        await send_message(msg, lang.s.BAN_ID)
        

@Client.on_message(filters.command(CMD.AUTH))
async def auth(client:Client, msg:Message):
    if await check_user(msg.from_user.id, restricted=True):
        try:
            id = int(msg.text.split(" ", maxsplit=1)[1])
        except:
            await send_message(msg, lang.s.BAN_AUTH_FORMAT)
            return

        user = False if str(id).startswith('-100') else True
        if user:
            if id not in bot_set.auth_users:
                bot_set.auth_users.append(id)
                set_db.set_variable('AUTH_USERS', str(bot_set.auth_users))
            else: await send_message(msg, lang.s.USER_EXIST)
        else:
            if id not in bot_set.auth_chats:
                bot_set.auth_chats.append(id)
                set_db.set_variable('AUTH_CHATS', str(bot_set.auth_chats))
            else: await send_message(msg, lang.s.USER_EXIST)
        await send_message(msg, lang.s.AUTH_ID)


@Client.on_message(filters.command(CMD.LOG))
async def send_log(client:Client, msg:Message):
    if await check_user(msg.from_user.id, restricted=True):
        user = await fetch_user_details(msg)
        await send_message(
            user, 
            './bot/bot_logs.log',
            'doc'
        )


@Client.on_message(filters.command(CMD.SETVAR))
async def set_var(client: Client, msg: Message):
    if not await check_user(msg.from_user.id, restricted=True):
        return

    try:
        _, var_name, *var_value = msg.text.split(maxsplit=2)
        var_value = ' '.join(var_value).strip()

        if not var_value:
            return await msg.reply("Missing value. Usage: `/setvar VAR_NAME value`", quote=True)

        setattr(Config, var_name, var_value)
        set_db.set_variable(var_name, var_value)

        if var_name in DEEZER_VARS:
            try:
                await bot_set.deezer.session.close()
            except: pass
            await bot_set.login_deezer()
        if var_name in TIDAL_VARS:
            try:
                await bot_set.tidal.session.close()
            except: pass
            await bot_set.login_tidal()
        if var_name in QOBUZ_VARS:
            try:
                await bot_set.qobuz.session.close()
            except: pass
            await bot_set.login_qobuz()

        await msg.reply(f"✅ `{var_name}` updated and changes applied.", quote=True)

    except Exception as e:
        await msg.reply("Missing value. Usage: `/setvar VAR_NAME value`", quote=True)
