import os
import logging
from os import getenv
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
LOGGER = logging.getLogger(__name__)

if not os.environ.get("ENV"):
    load_dotenv('.env', override=True)



BASE_DYNAMIC_VARS = {'RCLONE_CONFIG','RCLONE_DEST','INDEX_LINK',}

TIDAL_VARS = {
    'TIDAL_MOBILE', 'TIDAL_MOBILE_TOKEN', 'TIDAL_ATMOS_MOBILE_TOKEN',
    'TIDAL_TV_TOKEN', 'TIDAL_TV_SECRET', 'TIDAL_CONVERT_M4A',
    'TIDAL_REFRESH_TOKEN', 'TIDAL_COUNTRY_CODE',
}

QOBUZ_VARS = {'QOBUZ_EMAIL', 'QOBUZ_PASSWORD', 'QOBUZ_USER', 'QOBUZ_TOKEN',}

DEEZER_VARS = {'DEEZER_EMAIL', 'DEEZER_PASSWORD', 'DEEZER_BF_SECRET', 'DEEZER_ARL',}

DYNAMIC_VARS = BASE_DYNAMIC_VARS | TIDAL_VARS | QOBUZ_VARS | DEEZER_VARS


class Config(object):
#--------------------

# MAIN BOT VARIABLES

#--------------------
    try:
        TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
        APP_ID = int(getenv("APP_ID"))
        API_HASH = getenv("API_HASH")
        DATABASE_URL = getenv("DATABASE_URL")
        BOT_USERNAME = getenv("BOT_USERNAME")
        ADMINS = set(int(x) for x in getenv("ADMINS").split())
    except:
        LOGGER.warning("BOT : Essential Configs are missing")
        exit(1)


#--------------------

# BOT WORKING DIRECTORY

#--------------------
    # For pyrogram temp files
    WORK_DIR = getenv("WORK_DIR", "./bot/")
    # Just name of the Downloads Folder
    DOWNLOADS_FOLDER = getenv("DOWNLOADS_FOLDER", "DOWNLOADS")
    DOWNLOAD_BASE_DIR = WORK_DIR + DOWNLOADS_FOLDER
    LOCAL_STORAGE = getenv("LOCAL_STORAGE", DOWNLOAD_BASE_DIR)
#--------------------

# FILE/FOLDER NAMING

#--------------------
    PLAYLIST_NAME_FORMAT = getenv("PLAYLIST_NAME_FORMAT", "{title} - Playlist")
    #ALBUM_NAME_FORMAT = getenv("ALBUM_PATH_FORMAT", "{album} - {albumartist}")
    TRACK_NAME_FORMAT = getenv("TRACK_NAME_FORMAT", "{title} - {artist}")
#--------------------

# RCLONE / INDEX

#--------------------
    RCLONE_CONFIG = getenv("RCLONE_CONFIG", None)
    # No trailing slashes '/' for both index and rclone_dest
    # Example for RCLONE_DEST : remote:yourfolder
    RCLONE_DEST = getenv("RCLONE_DEST", None)
    INDEX_LINK = getenv('INDEX_LINK', None)
#--------------------

# QOBUZ

#--------------------
    QOBUZ_EMAIL = getenv("QOBUZ_EMAIL", None)
    QOBUZ_PASSWORD = getenv("QOBUZ_PASSWORD", None)
    QOBUZ_USER = getenv("QOBUZ_USER", None)
    QOBUZ_TOKEN = getenv("QOBUZ_TOKEN", None)
#--------------------

# DEEZER

#--------------------
    DEEZER_EMAIL = getenv("DEEZER_EMAIL", None)
    DEEZER_PASSWORD = getenv("DEEZER_PASSWORD", None)
    DEEZER_BF_SECRET = getenv("DEEZER_BF_SECRET", None)
    #DEEZER_TRACK_URL_KEY = getenv("DEEZER_TRACK_URL_KEY", None)
    DEEZER_ARL = getenv("DEEZER_ARL", None)
#--------------------

# TIDAL

#--------------------
    ENABLE_TIDAL = getenv("ENABLE_TIDAL", None)
    TIDAL_MOBILE = getenv("TIDAL_MOBILE", None) # only use email pass in mobile session
    TIDAL_MOBILE_TOKEN = getenv("TIDAL_MOBILE_TOKEN", None)
    TIDAL_ATMOS_MOBILE_TOKEN = getenv("TIDAL_ATMOS_MOBILE_TOKEN", None)
    TIDAL_TV_TOKEN = getenv("TIDAL_TV_TOKEN", None)
    TIDAL_TV_SECRET = getenv("TIDAL_TV_SECRET", None)
    TIDAL_CONVERT_M4A = getenv("TIDAL_CONVERT_M4A", False)
    TIDAL_REFRESH_TOKEN = getenv("TIDAL_REFRESH_TOKEN", None)
    TIDAL_COUNTRY_CODE = getenv("TIDAL_COUNTRY_CODE", None) # example CA for Canada
#--------------------

# CONCURRENT

#--------------------
    MAX_WORKERS = int(getenv("MAX_WORKERS", 5))
