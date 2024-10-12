from config import Config
import bot.helpers.translations as lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def links_button(rclone, index):
    inline_keyboard = []

    if rclone:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=lang.s.RCLONE_LINK,
                    url=rclone
                )
            ]
        )

    if Config.INDEX_LINK:
        if index:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=lang.s.INDEX_LINK,
                        url=index
                    )
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard)