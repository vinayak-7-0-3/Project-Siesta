import os
import json
import requests

from config import Config
from bot.logger import LOGGER

from .helpers.database.pg_impl import set_db
from .helpers.qobuz.qopy import qobuz_api
from .helpers.deezer.dzapi import deezerapi


class BotSettings:
    def __init__(self):
        self.deezer = False
        self.qobuz = False
        self.admins = Config.ADMINS

        db_users, _ = set_db.get_variable('AUTH_USERS')
        self.auth_users = json.loads(db_users) if db_users else []
        db_chats, _ = set_db.get_variable('AUTH_CHATS')
        self.auth_chats = json.loads(db_chats) if db_chats else []

        self.rclone = False
        self.check_upload_mode()

        spam, _ = set_db.get_variable('ANTI_SPAM') #bool
        self.anti_spam = spam if spam else 'OFF'

        public, _ = set_db.get_variable('BOT_PUBLIC') #bool
        self.bot_public = True if public else False

        lang, _ = set_db.get_variable('BOT_LANGUAGE') #str
        self.bot_lang = lang if lang else 'en'

        # post photo of album/artist
        art_poster, _ = set_db.get_variable('ART_POSTER') #bool
        self.art_poster = True if art_poster else False

        playlist_sort, _ = set_db.get_variable("PLAYLIST_SORT")
        self.playlist_sort = playlist_sort if playlist_sort else False
        # disable returning links for sorted playlist for cleaner chat
        disable_sort_link, _ = set_db.get_variable("PLAYLIST_LINK_DISABLE")
        #self.disable_sort_link = disable_sort_link if disable_sort_link else False
        self.disable_sort_link = True

        # Multithreaded downloads
        artist_batch, _ = set_db.get_variable("ARTIST_BATCH_UPLOAD")
        self.artist_batch = artist_batch if artist_batch else False
        playlist_conc, _ = set_db.get_variable("PLAYLIST_CONCURRENT")
        self.playlist_conc = playlist_conc if playlist_conc else False 
        
        link_option, _ = set_db.get_variable('RCLONE_LINK_OPTIONS') #str
        self.link_options = link_option if self.rclone and link_option else 'False'

        #TODO
        self.album_sep_zip = False #For artists download
        self.album_zip = False
        self.playlist_zip = False
        self.artist_zip = False


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
                    LOGGER.info(f"DEEZER : Subscription - {deezerapi.user['OFFER_NAME']}")
                else:
                    try:
                        await deezerapi.session.close()
                    except:pass
            else:
                LOGGER.error('DEEZER : Check BF_SECRET and TRACK_URL_KEY')

bot_set = BotSettings()