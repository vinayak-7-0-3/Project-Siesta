import os

from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

from bot.tgclient import aio
from bot.settings import bot_set


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


async def fetch_user_details(msg: Message, reply=False) -> dict:
    """
    args:
        msg - pyrogram Message()
        reply - if user message was reply to another message
    """
    details = user_details.copy()

    details['user_id'] = msg.from_user.id
    details['name'] = msg.from_user.first_name
    if msg.from_user.username:
        details['user_name'] = msg.from_user.username
    else:
        details['user_name'] = msg.from_user.mention()
    details['r_id'] = msg.reply_to_message.id if reply else msg.id
    details['chat_id'] = msg.chat.id
    try:
        details['bot_msg'] = msg.id
    except:
        pass
    return details


async def check_user(uid=None, msg=None, restricted=False) -> bool:
    """
    Args:
        uid - User ID (only needed for restricted access)
        msg - Pyrogram Message (for getting chatid and userid)
        restricted - Access only to admins (bool)
    Returns:
        True - Can access
        False - Cannot Access 
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


async def antiSpam(uid=None, cid=None, revoke=False) -> bool:
    """
    Checks if user/chat in waiting mode(anti spam)
    Args
        uid: User id (int)
        cid: Chat id (int)
        revoke: bool (if to revoke the given ID)
    Returns:
        True - if spam
        False - if not spam
    """
    if revoke:
        if bot_set.anti_spam == 'CHAT+':
            if cid in current_user:
                current_user.remove(cid)
        elif bot_set.anti_spam == 'USER':
            if uid in current_user:
                current_user.remove(uid)
    else:
        if bot_set.anti_spam == 'CHAT+':
            if cid in current_user:
                return True
            else:
                current_user.append(cid)
        elif bot_set.anti_spam == 'USER':
            if uid in current_user:
                return True
            else:
                current_user.append(uid)
        return False



async def send_message(user, item, itype='text', caption=None, markup=None, chat_id=None, \
        thumb=None, meta=None):
    """
    user: user details (dict)
    item: to send
    itype: pic|doc|text|audio (str)
    caption: text
    markup: buttons
    chat_id: if override chat from user details
    thumb: thumbnail for sending audio
    meta: metadata for the audio file
    """
    if not isinstance(user, dict):
        user = await fetch_user_details(user)
    chat_id = chat_id if chat_id else user['chat_id']

    if itype == 'text':
        msg = await aio.send_message(
            chat_id=chat_id,
            text=item,
            reply_to_message_id=user['r_id'],
            reply_markup=markup,
            disable_web_page_preview=True
        )
        
    elif itype == 'doc':
        msg = await aio.send_document(
            chat_id=chat_id,
            document=item,
            caption=caption,
            reply_to_message_id=user['r_id']
        )

    elif itype == 'audio':
        msg = await aio.send_audio(
            chat_id=chat_id,
            audio=item,
            caption=caption,
            duration=int(meta['duration']),
            performer=meta['artist'],
            title=meta['title'],
            thumb=thumb,
            reply_to_message_id=user['r_id']
        )
        os.remove(thumb)

    elif itype == 'pic':
        msg = await aio.send_photo(
            chat_id=chat_id,
            photo=item,
            caption=caption,
            reply_to_message_id=user['r_id']
        )

    return msg


async def edit_message(msg:Message, text, markup=None):
    try:
        edited = await msg.edit_text(
            text=text,
            reply_markup=markup,
            disable_web_page_preview=True
        )
        return edited
    except MessageNotModified:
        return None