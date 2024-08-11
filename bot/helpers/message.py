import os

from ..tgclient import aio

from .utils import fetch_user_details


async def send_message(user, item, itype='text', caption=None, markup=None, chat_id=None, \
        thumb=None, meta=None):
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
        pass

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

async def edit_message(user, text, msg_id=None, markup=None):
    if not isinstance(user, dict):
        user = await fetch_user_details(user)
    msg_id = user['bot_msg'] if not msg_id else msg_id
    msg = await aio.edit_message_text(
        chat_id=user['chat_id'],
        message_id=msg_id,
        text=text,
        reply_markup=markup,
        disable_web_page_preview=True
    )
    return msg