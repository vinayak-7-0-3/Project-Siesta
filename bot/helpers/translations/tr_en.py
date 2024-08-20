class EN(object):

#----------------
#
# BASICS
#
#----------------
    WELCOME_MSG = "Hello {}"
    DOWNLOADING = 'Downloading........'
    DOWNLOAD_PROGRESS = 'Downloading {} of {}'
    UPLOADING = 'Uploading........'
    TASK_COMPLETED = "Download Finished"




#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_PANEL = '<b>Welcome to Bot Settings</b>'

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
    TELEGRAM = 'Telegram'
    QOBUZ = 'Qobuz'
    DEEZER = 'Deezer'
    BOT_PUBLIC = 'Bot Public - {}'
    BOT_LANGUAGE = 'Language'
    ANTI_SPAM = 'Anit Spam - {}'

    ALBUM_ART_BUT = "Album Art : {}"

    QOBUZ_QUALITY_PANEL = '<b>Edit Qobuz Quality Here</b>'


#----------------
#
# ERRORS
#
#----------------
    ERR_NO_LINK = 'No link found :('
    ERR_LINK_RECOGNITION = "Sorry, couldn't recognise the given link."
    ERR_QOBUZ_NOT_STREAMABLE = "This track/album is not available to download."

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