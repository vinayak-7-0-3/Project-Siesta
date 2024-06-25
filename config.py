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
#--------------------

# FILE/FOLDER NAMING

#--------------------
    PLAYLIST_NAME_FORMAT = getenv("PLAYLIST_NAME_FORMAT", "{title} - Playlist")
    ALBUM_NAME_FORMAT = getenv("ALBUM_PATH_FORMAT", "{album} - {albumartist}")
    TRACK_NAME_FORMAT = getenv("TRACK_NAME_FORMAT", "{title} - {artist}")
#--------------------

# RCLONE

#--------------------
    RCLONE_CONFIG = getenv("RCLONE_CONFIG", None)
    RCLONE_DEST = getenv("RCLONE_DEST", 'remote:newfolder')
#--------------------

# LOGGING (Error/Info)

#--------------------
    LOG_CHAT = getenv("LOG_CHAT", "")
    LOG_ALL_INFO = getenv("LOG_ALL_INFO", "")
    CLEAR_LOG_FILE = getenv("CLEAR_LOG_FILE", False)