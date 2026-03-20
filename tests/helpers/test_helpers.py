from pyrogram import enums
from pyrogram.helpers import btn, ikb, kb, ntb
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def test_btn_supports_legacy_callback_data_with_password():
    button = btn("Confirm", "payload", "callback_data_with_password")

    assert button.text == "Confirm"
    assert button.callback_data == "payload"
    assert button.requires_password is True


def test_ikb_supports_legacy_callback_data_with_password_dict():
    markup = ikb([[{"text": "Confirm", "callback_data_with_password": "payload"}]])
    button = markup.inline_keyboard[0][0]

    assert button.text == "Confirm"
    assert button.callback_data == "payload"
    assert button.requires_password is True


def test_ntb_preserves_legacy_requires_password_shorthand():
    button = InlineKeyboardButton("Confirm", callback_data="payload", requires_password=True)

    assert ntb(button) == ("Confirm", "payload", "callback_data_with_password")


def test_ntb_keeps_empty_switch_inline_query():
    button = InlineKeyboardButton("Search", switch_inline_query="")

    assert ntb(button) == ("Search", "", "switch_inline_query")


def test_ntb_returns_dict_for_extra_metadata():
    button = InlineKeyboardButton(
        "Docs",
        url="https://pyrogram.org",
        style=enums.ButtonStyle.PRIMARY,
    )

    assert ntb(button) == {
        "text": "Docs",
        "url": "https://pyrogram.org",
        "style": enums.ButtonStyle.PRIMARY,
    }


def test_kb_returns_reply_keyboard_markup():
    markup = kb([["One"]], resize_keyboard=True)

    assert isinstance(markup, ReplyKeyboardMarkup)
    assert isinstance(markup.keyboard[0][0], KeyboardButton)
    assert markup.keyboard[0][0].text == "One"
    assert markup.resize_keyboard is True
