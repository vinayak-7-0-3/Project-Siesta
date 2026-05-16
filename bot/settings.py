import os
import json

import requests

from bot import LOGGER, Config

from .helpers.translations import set_lang
from .helpers.database.pg_impl import settings_db
from bot.utils.string import encrypt_string

from bot.models.uploader import UploaderTypes


class BotSettings:
    def __init__(self):
        self.admins = Config.ADMINS

        self.bot_lang= self._get_db_value('BOT_LANGUAGE','en')
        set_lang(self.bot_lang)

        self.auth_users = json.loads(self._get_db_value('AUTH_USERS', '[]'))
        self.auth_chats = json.loads(self._get_db_value('AUTH_CHATS', '[]'))

        self.rclone = False
        self._check_upload_mode()

        self.anti_spam = self._get_db_value('ANTI_SPAM', 'OFF')

        self.bot_public = self._get_db_value('BOT_PUBLIC', type_=bool)

        # post photo of album/artist
        self.art_poster = self._get_db_value('ART_POSTER', type_=bool)

        self.playlist_sort = self._get_db_value('PLAYLIST_SORT', type_=bool)
        # disable returning links for sorted playlist for cleaner chat
        self.disable_sort_link = self._get_db_value('PLAYLIST_LINK_DISABLE', type_=bool)

        # Multithreaded downloads
        self.artist_batch = self._get_db_value('ARTIST_BATCH_UPLOAD', type_=bool)
        self.playlist_conc = self._get_db_value('PLAYLIST_CONCURRENT', type_=bool)
        
        self.link_options = self._get_db_value('RCLONE_LINK_OPTIONS', 'False')

        self.album_zip = self._get_db_value('ALBUM_ZIP', type_=bool)
        self.playlist_zip = self._get_db_value('PLAYLIST_ZIP', type_=bool)
        self.artist_zip = self._get_db_value('ARTIST_ZIP', type_=bool)
        
        self.clients = []


    def _get_db_value(self, var: str, default=None, type_: type[str] | type[bool]=str):
        value, _ = settings_db.get_variable(var)
        if type_ is bool:
            return True if value else False
        return value if value else default


    def _check_upload_mode(self):
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
            
        db_upload = self._get_db_value('UPLOAD_MODE')
        if self.rclone and db_upload == 'RCLONE':
            self.upload_mode = UploaderTypes.RCLONE
        elif db_upload == 'Telegram' or db_upload == 'Local':
            self.upload_mode = UploaderTypes(db_upload)
        else:
            self.upload_mode = UploaderTypes.LOCAL #force local even if set to rclone when config missing


    async def save_tidal_login(self, session):
        data = {
            "user_id" : session.user_id,
            "refresh_token" : session.refresh_token,
            "country_code" : session.country_code
        }

        txt = json.dumps(data)
        settings_db.set_variable("TIDAL_AUTH_DATA", 0, True, encrypt_string(txt))


bot_settings = BotSettings()