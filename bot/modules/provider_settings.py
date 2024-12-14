import bot.helpers.translations as lang

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from config import Config

from ..settings import bot_set
from ..helpers.buttons.settings import *
from ..helpers.database.pg_impl import set_db
from ..helpers.tidal.tidal_api import tidalapi
from ..helpers.message import edit_message, check_user



@Client.on_callback_query(filters.regex(pattern=r"^providerPanel"))
async def provider_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message,
            lang.s.PROVIDERS_PANEL,
            providers_button()
        )


#----------------
# QOBUZ
#----------------
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


#----------------
# TIDAL
#----------------
@Client.on_callback_query(filters.regex(pattern=r"^tdP"))
async def tidal_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        await edit_message(
            cb.message,
            lang.s.TIDAL_PANEL,
            tidal_buttons()
        )
    
# show login button if not logged in
# show refresh button in case logged in exist (both tv and mobile)
@Client.on_callback_query(filters.regex(pattern=r"^tdAuth"))
async def tidal_auth_cb(c, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        sub = tidalapi.sub_type
        hires = True if tidalapi.mobile_hires else False
        atmos = True if tidalapi.mobile_atmos else False
        tv = True if tidalapi.tv_session else False

        await edit_message(
            cb.message,
            lang.s.TIDAL_AUTH_PANEL.format(sub, hires, atmos, tv),
            tidal_auth_buttons()
        )

@Client.on_callback_query(filters.regex(pattern=r"^tdLogin"))
async def tidal_login_cb(c:Client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        auth_url, err = await tidalapi.get_tv_login_url()
        if err:
            return await c.answer_callback_query(
                cb.id,
                err,
                True
            )
    
        await edit_message(
            cb.message,
            lang.s.TIDAL_AUTH_URL.format(auth_url),
            tidal_auth_buttons()
        )

        sub, err = await tidalapi.login_tv()
        if err:
            return await edit_message(
                cb.message,
                lang.s.ERR_LOGIN_TIDAL_TV_FAILED.format(err),
                tidal_auth_buttons()
            )
        if sub:
            bot_set.tidal = tidalapi
            bot_set.clients.append(tidalapi)

            await bot_set.save_tidal_login(tidalapi.tv_session)

            hires = True if tidalapi.mobile_hires else False
            atmos = True if tidalapi.mobile_atmos else False
            tv = True if tidalapi.tv_session else False
            await edit_message(
                cb.message,
                lang.s.TIDAL_AUTH_PANEL.format(sub, hires, atmos, tv) + '\n' + lang.s.TIDAL_AUTH_SUCCESSFULL,
                tidal_auth_buttons()
            )

@Client.on_callback_query(filters.regex(pattern=r"^tdRemove"))
async def tidal_remove_login_cb(c:Client, cb:CallbackQuery):
    if await check_user(cb.from_user.id, restricted=True):
        set_db.set_variable("TIDAL_AUTH_DATA", 0, True, None)

        tidalapi.tv_session = None
        tidalapi.mobile_atmos = None
        tidalapi.mobile_hires = None
        tidalapi.sub_type = None

        await tidalapi.session.close()
        bot_set.tidal = None

        await c.answer_callback_query(
            cb.id,
            lang.s.TIDAL_REMOVED_SESSION,
            True
        )

        await tidal_auth_cb(c, cb)

