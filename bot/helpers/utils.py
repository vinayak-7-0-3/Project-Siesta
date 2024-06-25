from .settings import bot_set

from config import Config
from pyrogram.types import Message

current_user = []

user_details = {
    'user_id': None,
    'name': None, # Name of the user 
    'user_name': None, # Username of the user
    'r_id': None, # Reply to message id
    'chat_id': None,
    'provider': None,
    'bot_msg': None,
    'link': None,
    'override' : None # To skip checking media exist
}


async def fetch_user_details(msg: Message, reply=False, provider=None):
    details = user_details.copy()

    details['user_id'] = msg.from_user.id
    details['name'] = msg.from_user.first_name
    if msg.from_user.username:
        details['user_name'] = msg.from_user.username
    else:
        details['user_name'] = msg.from_user.mention()
    details['r_id'] = msg.reply_to_message.id if reply else msg.id
    details['chat_id'] = msg.chat.id
    if provider:
        details['provider'] = provider
    try:
        details['bot_msg'] = msg.id
    except:
        pass
    return details


async def check_user(uid=None, msg=None, restricted=False):
    """
    uid - User ID (only needed for restricted access)
    msg - Pyrogram Message (for getting chatid and userid)
    restricted - Access only to admins (bool)
    """
    if restricted:
        if uid in bot_set.admins:
            return True
    else:
        if bot_set.bot_public:
            return True
        else:
            all_chats = list(bot_set.admins) + bot_set.auth_chats + bot_set.auth_users 
            if msg.from_user.id in all_chats:
                return True
            elif msg.chat.id in all_chats:
                return True

    return False


async def antiSpam(uid, cid) -> bool:
    """
    Args
        uid: User id
        cid: Chat id
    Returns:
        True - if spam
        False - if not spam
    """
    if bot_set.anti_spam == 'CHAT+':
        if cid in current_user:
            return True
        elif uid in current_user:
            return True
    elif bot_set.anti_spam == 'USER':
        if uid in current_user:
            return True
    else:
        return False