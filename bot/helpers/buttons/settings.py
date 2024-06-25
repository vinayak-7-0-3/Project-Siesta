from ..translations import lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

exit_button = [
    [
        InlineKeyboardButton(text=lang.MAIN_MENU_BUTTON, callback_data="main_menu"),
        InlineKeyboardButton(text=lang.CLOSE_BUTTON, callback_data="close")
    ]
]

def main_menu():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.TELEGRAM,
                callback_data='tgPanel'
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def tg_button(bot_public, anti_spam):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.BOT_PUBLIC.format(bot_public),
                callback_data='botPublic'
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.BOT_LANGUAGE,
                callback_data='botLang'
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.ANTI_SPAM.format(anti_spam),
                callback_data='antiSpam'
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)
