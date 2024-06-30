import os

from ..tgclient import aio

from .utils import fetch_user_details


async def send_message(details, item, type='text', caption=None, markup=None, chat_id=None, \
        thumb=None, meta=None):
    if not isinstance(details, dict):
        details = await fetch_user_details(details)
    chat_id = chat_id if chat_id else details['chat_id']

    if type == 'text':
        msg = await aio.send_message(
            chat_id=chat_id,
            text=item,
            reply_to_message_id=details['r_id'],
            reply_markup=markup,
            disable_web_page_preview=True
        )
        
    elif type == 'doc':
        pass

    elif type == 'audio':
        msg = await aio.send_audio(
            chat_id=chat_id,
            audio=item,
            caption=caption,
            duration=int(meta['duration']),
            performer=meta['artist'],
            title=meta['title'],
            thumb=thumb,
            reply_to_message_id=details['r_id']
        )
        os.remove(thumb)

    elif type == 'pic':
        msg = await aio.send_photo(
            chat_id=chat_id,
            photo=item,
            caption=caption,
            reply_to_message_id=details['r_id']
        )

    return msg

async def edit_message(details, text, msg_id=None, markup=None):
    if not isinstance(details, dict):
        details = await fetch_user_details(details)
    msg_id = details['bot_msg'] if not msg_id else msg_id
    msg = await aio.edit_message_text(
        chat_id=details['chat_id'],
        message_id=msg_id,
        text=text,
        reply_markup=markup,
        disable_web_page_preview=True
    )
    return msg