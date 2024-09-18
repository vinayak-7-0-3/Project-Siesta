import psycopg2
import datetime
import psycopg2.extras
from .pg_db import DataBaseHandle

from config import Config

#special_characters = ['!','#','$','%', '&','@','[',']',' ',']','_', ',', '.', ':', ';', '<', '>', '?', '\\', '^', '`', '{', '|', '}', '~']

"""
SETTINGS VARS

AUTH_CHATS - Chats where bot is allowed (str)
AUTH_USERS - Users who can use bot (str)
UPLOAD_MODE - RCLONE|Telegram|Local (str)
ANTI_SPAM - OFF|CHAT+|USER (str)
BOT_PUBLIC - True|False (bool)
BOT_LANGUAGE - (str) ISO 639-1 Codes Only
ART_POSTER - True|False (bool)
RCLONE_LINK_OPTIONS - False|RCLONE|Index|Both (str)
PLAYLIST_SORT - (bool)
ARTIST_BATCH_UPLOAD - (bool)
PLAYLIST_CONCURRENT - (bool)
PLAYLIST_LINK_DISABLE - Disable links for sorted playlist (bool)

QOBUZ_QUALITY - (int)
"""

class BotSettings(DataBaseHandle):

    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)

        settings_schema = """CREATE TABLE IF NOT EXISTS bot_settings (
            id SERIAL PRIMARY KEY NOT NULL,
            var_name VARCHAR(50) NOT NULL UNIQUE,
            var_value VARCHAR(2000) DEFAULT NULL,
            vtype VARCHAR(20) DEFAULT NULL,
            blob_val BYTEA DEFAULT NULL,
            date_changed TIMESTAMP NOT NULL
        )"""

        cur = self.scur()
        try:
            cur.execute(settings_schema)
        except psycopg2.errors.UniqueViolation:
            pass

        self._conn.commit()
        self.ccur(cur)

    def set_variable(self, var_name, var_value, update_blob=False, blob_val=None):
        vtype = "str"
        if isinstance(var_value, bool):
            vtype = "bool"
        elif isinstance(var_value, int):
            vtype = "int"

        if update_blob:
            vtype = "blob"

        sql = "SELECT * FROM bot_settings WHERE var_name=%s"
        cur = self.scur()

        cur.execute(sql, (var_name,))
        if cur.rowcount > 0:
            if not update_blob:
                sql = "UPDATE bot_settings SET var_value=%s , vtype=%s WHERE var_name=%s"
            else:
                sql = "UPDATE bot_settings SET blob_val=%s , vtype=%s WHERE var_name=%s"
                var_value = blob_val

            cur.execute(sql, (var_value, vtype, var_name))
        else:
            if not update_blob:
                sql = "INSERT INTO bot_settings(var_name,var_value,date_changed,vtype) VALUES(%s,%s,%s,%s)"
            else:
                sql = "INSERT INTO bot_settings(var_name,blob_val,date_changed,vtype) VALUES(%s,%s,%s,%s)"
                var_value = blob_val

            cur.execute(sql, (var_name, var_value, datetime.datetime.now(), vtype))

        self.ccur(cur)

    def get_variable(self, var_name):
        sql = "SELECT * FROM bot_settings WHERE var_name=%s"
        cur = self.scur()

        cur.execute(sql, (var_name,))
        if cur.rowcount > 0:
            row = cur.fetchone()
            vtype = row[3]
            val = row[2]
            if vtype == "int":
                val = int(row[2])
            elif vtype == "str":
                val = str(row[2])
            elif vtype == "bool":
                if row[2] == "true":
                    val = True
                else:
                    val = False

            return val, row[4]
        else:
            return None, None

        self.ccur(cur)

    def __del__(self):
        super().__del__()


set_db = BotSettings()