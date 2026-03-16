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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import TYPE_CHECKING, Union

from pyrogram import raw
from pyrogram.raw.core import BaseTypeMeta


if TYPE_CHECKING:
    KeyboardButton = Union[raw.types.InputKeyboardButtonRequestPeer, raw.types.InputKeyboardButtonUrlAuth, raw.types.InputKeyboardButtonUserProfile, raw.types.KeyboardButton, raw.types.KeyboardButtonBuy, raw.types.KeyboardButtonCallback, raw.types.KeyboardButtonCopy, raw.types.KeyboardButtonGame, raw.types.KeyboardButtonRequestGeoLocation, raw.types.KeyboardButtonRequestPeer, raw.types.KeyboardButtonRequestPhone, raw.types.KeyboardButtonRequestPoll, raw.types.KeyboardButtonSimpleWebView, raw.types.KeyboardButtonSwitchInline, raw.types.KeyboardButtonUrl, raw.types.KeyboardButtonUrlAuth, raw.types.KeyboardButtonUserProfile, raw.types.KeyboardButtonWebView]
else:
    # noinspection PyRedeclaration
    class KeyboardButton(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 18 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputKeyboardButtonRequestPeer <pyrogram.raw.types.InputKeyboardButtonRequestPeer>`
            - :obj:`InputKeyboardButtonUrlAuth <pyrogram.raw.types.InputKeyboardButtonUrlAuth>`
            - :obj:`InputKeyboardButtonUserProfile <pyrogram.raw.types.InputKeyboardButtonUserProfile>`
            - :obj:`KeyboardButton <pyrogram.raw.types.KeyboardButton>`
            - :obj:`KeyboardButtonBuy <pyrogram.raw.types.KeyboardButtonBuy>`
            - :obj:`KeyboardButtonCallback <pyrogram.raw.types.KeyboardButtonCallback>`
            - :obj:`KeyboardButtonCopy <pyrogram.raw.types.KeyboardButtonCopy>`
            - :obj:`KeyboardButtonGame <pyrogram.raw.types.KeyboardButtonGame>`
            - :obj:`KeyboardButtonRequestGeoLocation <pyrogram.raw.types.KeyboardButtonRequestGeoLocation>`
            - :obj:`KeyboardButtonRequestPeer <pyrogram.raw.types.KeyboardButtonRequestPeer>`
            - :obj:`KeyboardButtonRequestPhone <pyrogram.raw.types.KeyboardButtonRequestPhone>`
            - :obj:`KeyboardButtonRequestPoll <pyrogram.raw.types.KeyboardButtonRequestPoll>`
            - :obj:`KeyboardButtonSimpleWebView <pyrogram.raw.types.KeyboardButtonSimpleWebView>`
            - :obj:`KeyboardButtonSwitchInline <pyrogram.raw.types.KeyboardButtonSwitchInline>`
            - :obj:`KeyboardButtonUrl <pyrogram.raw.types.KeyboardButtonUrl>`
            - :obj:`KeyboardButtonUrlAuth <pyrogram.raw.types.KeyboardButtonUrlAuth>`
            - :obj:`KeyboardButtonUserProfile <pyrogram.raw.types.KeyboardButtonUserProfile>`
            - :obj:`KeyboardButtonWebView <pyrogram.raw.types.KeyboardButtonWebView>`
        """

        QUALNAME = "pyrogram.raw.base.KeyboardButton"
        __union_types__ = Union[raw.types.InputKeyboardButtonRequestPeer, raw.types.InputKeyboardButtonUrlAuth, raw.types.InputKeyboardButtonUserProfile, raw.types.KeyboardButton, raw.types.KeyboardButtonBuy, raw.types.KeyboardButtonCallback, raw.types.KeyboardButtonCopy, raw.types.KeyboardButtonGame, raw.types.KeyboardButtonRequestGeoLocation, raw.types.KeyboardButtonRequestPeer, raw.types.KeyboardButtonRequestPhone, raw.types.KeyboardButtonRequestPoll, raw.types.KeyboardButtonSimpleWebView, raw.types.KeyboardButtonSwitchInline, raw.types.KeyboardButtonUrl, raw.types.KeyboardButtonUrlAuth, raw.types.KeyboardButtonUserProfile, raw.types.KeyboardButtonWebView]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.icu/telegram/base/keyboard-button")
