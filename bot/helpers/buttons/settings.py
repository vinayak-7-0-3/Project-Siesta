from ..translations import lang
from bot.settings import bot_set
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
    if bot_set.qobuz:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=lang.QOBUZ,
                    callback_data='qbP'
                )
            ]
        )
    if bot_set.deezer:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=lang.DEEZER,
                    callback_data='dzP'
                )
            ]
        )
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def tg_button(bot_public, anti_spam, alb_art, upload):
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
        ],
        [
            InlineKeyboardButton(
                text=lang.ALBUM_ART_BUT.format(alb_art),
                callback_data='albArt'
            )
        ],
        [
            InlineKeyboardButton(
                text=f"Upload : {upload}",
                callback_data='upload'
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def qb_button(qualities:dict):
    inline_keyboard = []
    for quality in qualities.values():
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=quality,
                    callback_data=f"qbQ_{quality.replace('✅', '')}"
                )
            ]
        )
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)