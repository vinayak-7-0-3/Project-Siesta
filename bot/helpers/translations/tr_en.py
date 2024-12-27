class EN(object):
    __language__ = 'en'
#----------------
#
# BASICS
#
#----------------
    WELCOME_MSG = "Hello {}"
    DOWNLOADING = 'Downloading........'
    DOWNLOAD_PROGRESS = """
<b>╭─ Progress
│
├ {0}
│
├ Done : <code>{1} / {2}</code>
│
├ Title : <code>{3}</code>
│
╰─ Type : <code>{4}</code></b>
"""
    UPLOADING = 'Uploading........'
    ZIPPING = 'Zipping........'
    TASK_COMPLETED = "Download Finished"




#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_PANEL = '<b>Welcome to Bot Settings</b>'
    LANGUAGE_PANEL = 'Select bot language here'
    CORE_PANEL = 'Edit main settings here'
    PROVIDERS_PANEL = 'Configure each platform seperartelty'

    TIDAL_PANEL = "Configure Tidal settings here"
    TIDAL_AUTH_PANEL = """
Manage auth of Tidal Account here

<b>Account :</b> <code>{}</code>
<b>Mobile HiRes :</b> <code>{}</code>
<b>Mobile Atmos :</b> <code>{}</code>
<b>TV/Auto : </b> <code>{}</code>
"""
    TIDAL_AUTH_URL = "Go to the below link for loggin in\n{}"
    TIDAL_AUTH_SUCCESSFULL = 'Succesfully logged in Tidal'
    TIDAL_REMOVED_SESSION = 'Successfully removed all sessions for Tidal'

    TELEGRAM_PANEL = """
<b>Telegram Settings</b>

Admins : {2}
Auth Users : {3}
Auth Chats : {4}
"""
    BAN_AUTH_FORMAT = 'Use /command {userid}'
    BAN_ID = 'Removed {}'
    USER_DOEST_EXIST = "This ID doesn't exist"
    USER_EXIST = 'This ID already exist'
    AUTH_ID = 'Successfully Authed'





#----------------
#
# BUTTONS
#
#----------------
    MAIN_MENU_BUTTON = 'MAIN MENU'
    CLOSE_BUTTON = 'CLOSE'
    PROVIDERS = 'PROVIDERS'
    TELEGRAM = 'Telegram'
    CORE = 'CORE'
    
    QOBUZ = 'Qobuz'
    DEEZER = 'Deezer'
    TIDAL = 'Tidal'

    BOT_PUBLIC = 'Bot Public - {}'
    BOT_LANGUAGE = 'Language'
    ANTI_SPAM = 'Anit Spam - {}'
    LANGUAGE = 'Language'
    QUALITY = 'Quality'
    AUTHORIZATION = "Authorizations"

    POST_ART_BUT = "Art Poster : {}"
    SORT_PLAYLIST = 'Sort Playlist : {}'
    DISABLE_SORT_LINK = 'Disable Sort Link : {}'
    PLAYLIST_CONC_BUT = "Playlist Batch Download : {}"
    PLAYLIST_ZIP = 'Zip Playlist : {}'
    ARTIST_BATCH_BUT = 'Artist Batch Upload : {}'
    ARTIST_ZIP = 'Zip Artist : {}'
    ALBUM_ZIP = 'Zip Album : {}'

    QOBUZ_QUALITY_PANEL = '<b>Edit Qobuz Quality Here</b>'

    TIDAL_LOGIN_TV = 'Login TV'
    TIDAL_REMOVE_LOGIN = "Remove Login"
    TIDAL_REFRESH_SESSION = 'Refresh Auth'

    RCLONE_LINK = 'Direct Link'
    INDEX_LINK = 'Index Link'
#----------------
#
# ERRORS
#
#----------------
    ERR_NO_LINK = 'No link found :('
    ERR_LINK_RECOGNITION = "Sorry, couldn't recognise the given link."
    ERR_QOBUZ_NOT_STREAMABLE = "This track/album is not available to download."
    ERR_QOBUZ_NOT_AVAILABLE = "This track is not available in your region"
    ERR_LOGIN_TIDAL_TV_FAILED = "Login failed : {}"
#----------------
#
# ERRORS
#
#----------------
    WARNING_NO_TIDAL_TOKEN = 'No TV/Auto token-secret added'
#----------------
#
# TRACK & ALBUM POSTS
#
#----------------
    ALBUM_TEMPLATE = """
🎶 <b>Title :</b> {title}
👤 <b>Artist :</b> {artist}
📅 <b>Release Date :</b> {date}
🔢 <b>Total Tracks :</b> {totaltracks}
📀 <b>Total Volumes :</b> {totalvolume}
💫 <b>Quality :</b> {quality}
📡 <b>Provider :</b> {provider}
🔞 <b>Explicit :</b> {explicit}
"""

    PLAYLIST_TEMPLATE = """
🎶 <b>Title :</b> {title}
🔢 <b>Total Tracks :</b> {totaltracks}
💫 <b>Quality :</b> {quality}
📡 <b>Provider :</b> {provider}
"""

    SIMPLE_TITLE = """
Name : {0}
Type : {1}
Provider : {2}
"""

ARTIST_TEMPLATE = """
👤 <b>Artist :</b> {artist}
💫 <b>Quality :</b> {quality}
📡 <b>Provider :</b> {provider}
"""
