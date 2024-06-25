from bot import CMD
from pyrogram import Client, filters
from ..helpers.translations import lang
from ..helpers.message import send_message

@Client.on_message(filters.command(CMD.START))
async def start(bot, update):
    msg = await bot.send_message(
        chat_id=update.chat.id,
        text=lang.WELCOME_MSG.format(
            update.from_user.first_name
        ),
        reply_to_message_id=update.id
    )