#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import List, Sequence, Tuple, Union, Optional, Dict, Any

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ForceReply,
)


def ikb(
    rows: Optional[
        Sequence[
            Sequence[
                Union[
                    InlineKeyboardButton,
                    Dict[str, Any],
                    Tuple[str, Any, str],
                    Tuple[str, Any],
                ]
            ]
        ]
    ] = None
) -> InlineKeyboardMarkup:
    """Build an InlineKeyboardMarkup from a matrix description.

    Parameters:
        rows: A sequence of rows; each row is a sequence of buttons. Each button can be:
            - InlineKeyboardButton: used as-is
            - dict: must contain "text" and exactly one optional field (see btn())
            - (text, value, field): explicit field form, see btn()
            - (text, value): shorthand for (text, value, "callback_data")

    Returns:
        InlineKeyboardMarkup instance.

    Note:
        InlineKeyboardButton requires exactly one optional field to be set.
    """
    if rows is None:
        rows = []

    keyboard_rows: List[List[InlineKeyboardButton]] = []
    for row in rows:
        line: List[InlineKeyboardButton] = []
        for button in row:
            if isinstance(button, InlineKeyboardButton):
                built = button
            elif isinstance(button, dict):
                if "text" not in button:
                    raise ValueError("Inline button dict must include 'text'")
                # # Validate exactly one optional field
                # opt_keys = [k for k in button.keys() if k != "text"]
                # if len(opt_keys) != 1:
                #     raise ValueError("Inline button dict must include exactly one optional field")
                built = InlineKeyboardButton(**button)
            elif isinstance(button, tuple):
                if len(button) == 2:
                    text, value = button
                    built = btn(text, value, "callback_data")
                elif len(button) == 3:
                    text, value, field = button
                    built = btn(text, value, field)
                else:
                    raise ValueError("Inline button tuple must be (text, value) or (text, value, field)")
            else:
                raise TypeError("Button must be InlineKeyboardButton, dict or tuple")
            line.append(built)
        keyboard_rows.append(line)
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    # return {'inline_keyboard': lines}


def btn(text: str, value: Any = None, type: str = "callback_data") -> InlineKeyboardButton:
    """Create an InlineKeyboardButton enforcing the single-optional-field rule.

    Parameters:
        text: Button text.
        value: Value of the selected optional field; type depends on the field.
        type: One of the supported optional fields:
              "callback_data", "url", "web_app", "login_url", "user_id",
              "switch_inline_query", "switch_inline_query_current_chat",
              "callback_game", "callback_data_with_password", "pay", "copy_text".

    Returns:
        InlineKeyboardButton.
    """
    allowed = {
        "callback_data",
        "url",
        "web_app",
        "login_url",
        "user_id",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "callback_data_with_password",
        "pay",
        "copy_text",
    }
    if type not in allowed:
        raise ValueError(f"Unsupported button field: {type}")
    if type == "pay" and value is not True:
        raise ValueError("'pay' button requires value=True")
    return InlineKeyboardButton(text, **{type: value})
    # return {'text': text, type: value}


# The inverse of above
def bki(keyboard: InlineKeyboardMarkup) -> List[List[Union[str, Tuple[str, str], Tuple[str, str, str]]]]:
    """Convert InlineKeyboardMarkup back to the tuple-based matrix format.

    Parameters:
        keyboard: InlineKeyboardMarkup to convert.

    Returns:
        A list of rows with button specs suitable for ikb().
    """
    lines: List[List[Union[str, Tuple[str, str], Tuple[str, str, str]]]] = []
    for row in keyboard.inline_keyboard:
        line = []
        for button in row:
            line.append(ntb(button))
        lines.append(line)
    return lines
    # return ikb() format


def ntb(button: InlineKeyboardButton) -> Union[Tuple[str, Any], Tuple[str, Any, str]]:
    """Normalize InlineKeyboardButton to tuple format used by btn().

    Parameters:
        button: InlineKeyboardButton.

    Returns:
        (text, value) for callback_data buttons, otherwise (text, value, type).
    """
    btn_type = None
    for candidate in (
        "callback_data",
        "url",
        "web_app",
        "login_url",
        "user_id",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "callback_data_with_password",
        "pay",
        "copy_text",
    ):
        value = getattr(button, candidate)
        if value:
            btn_type = candidate
            break
    if btn_type is None:
        raise ValueError("InlineKeyboardButton has no supported attributes set")

    if btn_type == "callback_data":
        return button.text, value
    return button.text, value, btn_type
    # return {'text': text, type: value}


def kb(rows: Optional[Sequence[Sequence[Union[str, KeyboardButton, dict]]]] = None, **kwargs) -> ReplyKeyboardMarkup:
    """Build a ReplyKeyboardMarkup from a matrix description.

    Parameters:
        rows: A sequence of rows; each row is a sequence of:
            - str: converted to KeyboardButton(text)
            - dict: unpacked as KeyboardButton(**dict)
            - KeyboardButton: used as-is
        kwargs: Additional ReplyKeyboardMarkup keyword args (e.g. resize_keyboard=True).

    Returns:
        ReplyKeyboardMarkup instance.
    """
    if rows is None:
        rows = []

    keyboard_rows: List[List[KeyboardButton]] = []
    for row in rows:
        line: List[KeyboardButton] = []
        for button in row:
            if isinstance(button, KeyboardButton):
                built = button
            elif isinstance(button, str):
                built = KeyboardButton(button)
            elif isinstance(button, dict):
                built = KeyboardButton(**button)
            else:
                raise TypeError("Button must be str, dict or KeyboardButton")
            line.append(built)
        keyboard_rows.append(line)
    return ReplyKeyboardMarkup(keyboard=keyboard_rows, **kwargs)


kbtn = KeyboardButton
"""
Create a KeyboardButton.
"""


def force_reply(selective: bool = True) -> ForceReply:
    """Create a ForceReply object.

    Parameters:
        selective: Whether to force reply for specific users only.

    Returns:
        ForceReply instance.
    """
    return ForceReply(selective=selective)


def array_chunk(input_array: Sequence, size: int) -> List[Sequence]:
    """Split a sequence into fixed-size chunks.

    Parameters:
        input_array: The sequence to split.
        size: Chunk size, must be > 0.

    Returns:
        A list of chunks (slices of the original sequence).
    """
    if size <= 0:
        raise ValueError("size must be > 0")
    return [input_array[i: i + size] for i in range(0, len(input_array), size)]