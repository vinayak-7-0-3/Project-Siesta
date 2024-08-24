from config import Config

from ..translations import lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def links_button(rclone, index):
    inline_keyboard = []

    if rclone:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=lang.RCLONE_LINK,
                    url=rclone
                )
            ]
        )

    if Config.INDEX_LINK:
        if index:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=lang.INDEX_LINK,
                        url=index
                    )
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard)