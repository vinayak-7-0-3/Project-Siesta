import os
import json
import base64
import requests

import bot.helpers.translations as lang

from config import Config
from bot.logger import LOGGER

from .helpers.database.pg_impl import set_db
from .helpers.qobuz.qopy import qobuz_api
from .helpers.deezer.dzapi import deezerapi
from .helpers.tidal.tidal_api import tidalapi
from .helpers.translations import lang_available


# For simple boolean values
def __getvalue__(var):
    value, _ = set_db.get_variable(var)
    return value if value else False

def __encrypt_string__(string):
    s = bytes(string, 'utf-8')
    s = base64.b64encode(s)
    return s

def __decrypt_string__(string):
    try:
        s = base64.b64decode(string)
        s = s.decode()
        return s
    except:
        return string



class BotSettings:
    def __init__(self):
        self.deezer = False
        self.qobuz = False
        self.tidal = False
        self.admins = Config.ADMINS

        self.set_language()

        db_users, _ = set_db.get_variable('AUTH_USERS')
        self.auth_users = json.loads(db_users) if db_users else []
        db_chats, _ = set_db.get_variable('AUTH_CHATS')
        self.auth_chats = json.loads(db_chats) if db_chats else []

        self.rclone = False
        self.check_upload_mode()

        spam, _ = set_db.get_variable('ANTI_SPAM') #string
        self.anti_spam = spam if spam else 'OFF'

        self.bot_public = __getvalue__('BOT_PUBLIC')

        # post photo of album/artist
        self.art_poster = __getvalue__('ART_POSTER')

        self.playlist_sort = __getvalue__('PLAYLIST_SORT')
        # disable returning links for sorted playlist for cleaner chat
        self.disable_sort_link = __getvalue__('PLAYLIST_LINK_DISABLE')

        # Multithreaded downloads
        self.artist_batch = __getvalue__('ARTIST_BATCH_UPLOAD')
        self.playlist_conc = __getvalue__('PLAYLIST_CONCURRENT')
        
        link_option, _ = set_db.get_variable('RCLONE_LINK_OPTIONS') #str
        self.link_options = link_option if self.rclone and link_option else 'False'

        self.album_zip = __getvalue__('ALBUM_ZIP')
        self.playlist_zip = __getvalue__('PLAYLIST_ZIP')
        self.artist_zip = __getvalue__('ARTIST_ZIP')

        self.clients = []

    def check_upload_mode(self):
        if os.path.exists('rclone.conf'):
            self.rclone = True
        elif Config.RCLONE_CONFIG:
            if Config.RCLONE_CONFIG.startswith('http'):
                rclone = requests.get(Config.RCLONE_CONFIG, allow_redirects=True)
                if rclone.status_code != 200:
                    LOGGER.info("RCLONE : Error retreiving file from Config URL")
                    self.rclone = False
                else:
                    with open('rclone.conf', 'wb') as f:
                        f.write(rclone.content)
                    self.rclone = True
            
        db_upload, _ = set_db.get_variable('UPLOAD_MODE')
        if self.rclone and db_upload == 'RCLONE':
            self.upload_mode = 'RCLONE'
        elif db_upload == 'Telegram' or db_upload == 'Local':
            self.upload_mode = db_upload
        else:
            self.upload_mode = 'Local'
    

    async def login_qobuz(self):
        if Config.QOBUZ_EMAIL or Config.QOBUZ_USER:
            try:
                await qobuz_api.login()
                self.qobuz = qobuz_api
                self.clients.append(qobuz_api)
                quality, _ = set_db.get_variable("QOBUZ_QUALITY")
                if quality:
                    bot_set.qobuz.quality = int(quality)
            except Exception as e:
                LOGGER.error(e)
    
    async def login_deezer(self):
        if Config.DEEZER_ARL or Config.DEEZER_EMAIL:
            if Config.DEEZER_BF_SECRET and Config.DEEZER_TRACK_URL_KEY:
                login = await deezerapi.login()
                if login:
                    self.deezer = deezerapi
                    self.clients.append(deezerapi)
                    LOGGER.info(f"DEEZER : Subscription - {deezerapi.user['OFFER_NAME']}")
                else:
                    try:
                        await deezerapi.session.close()
                    except:pass
            else:
                LOGGER.error('DEEZER : Check BF_SECRET and TRACK_URL_KEY')

    async def login_tidal(self):
        # only load the object if needed
        self.can_enable_tidal = Config.ENABLE_TIDAL
        if not self.can_enable_tidal:
            return

        _, refresh_token = set_db.get_variable("TIDAL_AUTH_DATA")
        loaded = False

        enable_mobile = Config.TIDAL_MOBILE
        # dont force login via email pass on each startup
        # only login using email when no session found on database
        if Config.TIDAL_EMAIL or Config.TIDAL_PASS:
            if refresh_token:
                pass
            if enable_mobile:
                pass 
        else:
            # check for any earlier logins
            if refresh_token:
                _, txt = set_db.get_variable("TIDAL_AUTH_DATA")
                data = json.loads(__decrypt_string__(txt))
                sub = await tidalapi.login_from_saved(data)
                if sub:
                    LOGGER.info("TIDAL : Loaded account - " + sub)
                    loaded = True

        if loaded: # no errors while loading
            self.tidal = tidalapi 
            self.clients.append(tidalapi) 

    async def save_tidal_login(self, session):
        data = {
            "user_id" : session.user_id,
            "refresh_token" : session.refresh_token,
            "country_code" : session.country_code
        }

        txt = json.dumps(data)
        set_db.set_variable("TIDAL_AUTH_DATA", 0, True, __encrypt_string__(txt))
        



    def set_language(self):
        db_lang, _ = set_db.get_variable('BOT_LANGUAGE') #str
        self.bot_lang = db_lang if db_lang else 'en'

        for item in lang_available:
            if item.__language__ == self.bot_lang:
                lang.s = item
                break


bot_set = BotSettings()