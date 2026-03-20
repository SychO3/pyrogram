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

from typing import Any, Dict, List, Optional, Sequence, Tuple, TypeVar, Union

from pyrogram import enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ForceReply,
)


INLINE_BUTTON_ACTION_FIELDS = (
    "callback_data",
    "url",
    "web_app",
    "login_url",
    "user_id",
    "switch_inline_query",
    "switch_inline_query_current_chat",
    "callback_game",
    "pay",
    "copy_text",
)

InlineButtonShortcut = Union[Tuple[str, Any], Tuple[str, Any, str]]
InlineButtonMapping = Dict[str, Any]
InlineButtonInput = Union[InlineKeyboardButton, InlineButtonMapping, InlineButtonShortcut]
InlineButtonOutput = Union[Dict[str, Any], InlineButtonShortcut]
ReplyButtonInput = Union[str, KeyboardButton, Dict[str, Any]]
Item = TypeVar("Item")


def _normalize_inline_button_kwargs(button_data: InlineButtonMapping) -> Dict[str, Any]:
    normalized = dict(button_data)
    callback_data_with_password = normalized.pop("callback_data_with_password", None)

    if callback_data_with_password is not None:
        if "callback_data" in normalized:
            raise ValueError(
                "Inline button dict must include either 'callback_data' or "
                "'callback_data_with_password', not both"
            )

        normalized["callback_data"] = callback_data_with_password

        if normalized.get("requires_password") not in (None, True):
            raise ValueError("'requires_password' must be True when using 'callback_data_with_password'")

        normalized["requires_password"] = True

    primary_fields = [
        field for field in INLINE_BUTTON_ACTION_FIELDS if normalized.get(field) is not None
    ]

    if len(primary_fields) != 1:
        raise ValueError(
            "Inline button dict must include exactly one action field: "
            + ", ".join(INLINE_BUTTON_ACTION_FIELDS)
        )

    if normalized.get("pay") is not None and normalized["pay"] is not True:
        raise ValueError("'pay' button requires value=True")

    if normalized.get("requires_password") and normalized.get("callback_data") is None:
        raise ValueError("'requires_password' can only be used with 'callback_data'")

    return normalized


def _build_inline_button(button_data: InlineButtonMapping) -> InlineKeyboardButton:
    if "text" not in button_data:
        raise ValueError("Inline button dict must include 'text'")

    return InlineKeyboardButton(**_normalize_inline_button_kwargs(button_data))


def _serialize_inline_button(button: InlineKeyboardButton) -> Dict[str, Any]:
    data: Dict[str, Any] = {"text": button.text}

    for field in INLINE_BUTTON_ACTION_FIELDS:
        value = getattr(button, field, None)
        if value is not None:
            data[field] = value

    if data.get("callback_data") is not None and getattr(button, "requires_password", None):
        data["callback_data_with_password"] = data.pop("callback_data")
    elif getattr(button, "requires_password", None) is not None:
        data["requires_password"] = button.requires_password

    if getattr(button, "icon_custom_emoji_id", None) is not None:
        data["icon_custom_emoji_id"] = button.icon_custom_emoji_id

    if getattr(button, "style", enums.ButtonStyle.DEFAULT) != enums.ButtonStyle.DEFAULT:
        data["style"] = button.style

    return data


def ikb(
    rows: Optional[
        Sequence[
            Sequence[
                InlineButtonInput
            ]
        ]
    ] = None
) -> InlineKeyboardMarkup:
    """Build an InlineKeyboardMarkup from a matrix description.

    Parameters:
        rows: A sequence of rows; each row is a sequence of buttons. Each button can be:
            - InlineKeyboardButton: used as-is
            - dict: must contain "text" and exactly one action field (see btn())
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
        row_buttons: List[InlineKeyboardButton] = []

        for button in row:
            if isinstance(button, InlineKeyboardButton):
                built_button = button
            elif isinstance(button, dict):
                built_button = _build_inline_button(button)
            elif isinstance(button, tuple):
                if len(button) == 2:
                    text, value = button
                    built_button = btn(text, value, "callback_data")
                elif len(button) == 3:
                    text, value, field = button
                    built_button = btn(text, value, field)
                else:
                    raise ValueError("Inline button tuple must be (text, value) or (text, value, field)")
            else:
                raise TypeError("Button must be InlineKeyboardButton, dict or tuple")

            row_buttons.append(built_button)

        keyboard_rows.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def btn(
    text: str,
    value: Any = None,
    type: Optional[str] = None,
    *,
    field: Optional[str] = None,
    **button_kwargs: Any,
) -> InlineKeyboardButton:
    """Create an InlineKeyboardButton with helper-friendly field shorthands.

    Parameters:
        text: Button text.
        value: Value of the selected optional field; type depends on the field.
        type: Deprecated name for the selected field, kept for backwards compatibility.
        field: Preferred field name. One of the supported optional fields:
               "callback_data", "url", "web_app", "login_url", "user_id",
               "switch_inline_query", "switch_inline_query_current_chat",
               "callback_game", "callback_data_with_password", "pay", "copy_text".
        button_kwargs: Extra InlineKeyboardButton keyword args, e.g. requires_password,
                       style, icon_custom_emoji_id.

    Returns:
        InlineKeyboardButton.
    """
    if field is not None and type is not None and field != type:
        raise ValueError("'type' and 'field' must match when both are provided")

    button_field = field if field is not None else type or "callback_data"

    if button_field == "callback_data_with_password":
        if button_kwargs.get("requires_password") not in (None, True):
            raise ValueError("'requires_password' must be True for 'callback_data_with_password'")

        button_kwargs["requires_password"] = True
        button_field = "callback_data"

    if button_field not in INLINE_BUTTON_ACTION_FIELDS:
        raise ValueError(f"Unsupported button field: {button_field}")

    if button_field == "pay" and value is not True:
        raise ValueError("'pay' button requires value=True")

    return _build_inline_button({
        "text": text,
        button_field: value,
        **button_kwargs,
    })


# The inverse of above
def bki(keyboard: InlineKeyboardMarkup) -> List[List[InlineButtonOutput]]:
    """Convert InlineKeyboardMarkup back to the tuple-based matrix format.

    Parameters:
        keyboard: InlineKeyboardMarkup to convert.

    Returns:
        A list of rows with button specs suitable for ikb().
    """
    rows: List[List[InlineButtonOutput]] = []
    for row in keyboard.inline_keyboard:
        normalized_row: List[InlineButtonOutput] = []
        for button in row:
            normalized_row.append(ntb(button))
        rows.append(normalized_row)
    return rows


def ntb(button: InlineKeyboardButton) -> InlineButtonOutput:
    """Normalize InlineKeyboardButton to tuple format used by btn().

    Parameters:
        button: InlineKeyboardButton.

    Returns:
        (text, value) for callback_data buttons, (text, value, field) for simple buttons,
        or a dict when the button carries extra metadata such as style or icon.
    """
    button_field = None
    value = None

    for candidate in INLINE_BUTTON_ACTION_FIELDS:
        candidate_value = getattr(button, candidate, None)
        if candidate_value is not None:
            button_field = candidate
            value = candidate_value
            break

    if button_field is None:
        raise ValueError("InlineKeyboardButton has no supported attributes set")

    has_extra_metadata = any(
        (
            getattr(button, "requires_password", None),
            getattr(button, "icon_custom_emoji_id", None) is not None,
            getattr(button, "style", enums.ButtonStyle.DEFAULT) != enums.ButtonStyle.DEFAULT,
        )
    )

    if has_extra_metadata:
        serialized = _serialize_inline_button(button)
        if (
            set(serialized.keys()) == {"text", "callback_data_with_password"}
            and serialized["callback_data_with_password"] is not None
        ):
            return button.text, serialized["callback_data_with_password"], "callback_data_with_password"

        return serialized

    if button_field == "callback_data":
        return button.text, value
    return button.text, value, button_field


def kb(
    rows: Optional[Sequence[Sequence[ReplyButtonInput]]] = None,
    **markup_kwargs: Any,
) -> ReplyKeyboardMarkup:
    """Build a ReplyKeyboardMarkup from a matrix description.

    Parameters:
        rows: A sequence of rows; each row is a sequence of:
            - str: converted to KeyboardButton(text)
            - dict: unpacked as KeyboardButton(**dict)
            - KeyboardButton: used as-is
        markup_kwargs: Additional ReplyKeyboardMarkup keyword args
                       (e.g. resize_keyboard=True).

    Returns:
        ReplyKeyboardMarkup instance.
    """
    if rows is None:
        rows = []

    keyboard_rows: List[List[KeyboardButton]] = []
    for row in rows:
        row_buttons: List[KeyboardButton] = []
        for button in row:
            if isinstance(button, KeyboardButton):
                built_button = button
            elif isinstance(button, str):
                built_button = KeyboardButton(button)
            elif isinstance(button, dict):
                built_button = KeyboardButton(**button)
            else:
                raise TypeError("Button must be str, dict or KeyboardButton")

            row_buttons.append(built_button)

        keyboard_rows.append(row_buttons)

    return ReplyKeyboardMarkup(keyboard=keyboard_rows, **markup_kwargs)


# Backwards-compatible alias for KeyboardButton.
kbtn = KeyboardButton


def force_reply(selective: bool = True) -> ForceReply:
    """Create a ForceReply object.

    Parameters:
        selective: Whether to force reply for specific users only.

    Returns:
        ForceReply instance.
    """
    return ForceReply(selective=selective)


def array_chunk(items: Sequence[Item], size: int) -> List[Sequence[Item]]:
    """Split a sequence into fixed-size chunks.

    Parameters:
        items: The sequence to split.
        size: Chunk size, must be > 0.

    Returns:
        A list of chunks (slices of the original sequence).
    """
    if size <= 0:
        raise ValueError("size must be > 0")
    return [items[i: i + size] for i in range(0, len(items), size)]