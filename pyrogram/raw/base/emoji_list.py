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

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

# We need to dynamically set `__doc__` due to `sphinx`
EmojiList = Union[raw.types.EmojiList, raw.types.EmojiListNotModified]
EmojiList.__doc__ = """
    This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EmojiList <pyrogram.raw.types.EmojiList>`
            - :obj:`EmojiListNotModified <pyrogram.raw.types.EmojiListNotModified>`

    See Also:
        This object can be returned by 5 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetDefaultProfilePhotoEmojis <pyrogram.raw.functions.account.GetDefaultProfilePhotoEmojis>`
            - :obj:`account.GetDefaultGroupPhotoEmojis <pyrogram.raw.functions.account.GetDefaultGroupPhotoEmojis>`
            - :obj:`account.GetDefaultBackgroundEmojis <pyrogram.raw.functions.account.GetDefaultBackgroundEmojis>`
            - :obj:`account.GetChannelRestrictedStatusEmojis <pyrogram.raw.functions.account.GetChannelRestrictedStatusEmojis>`
            - :obj:`messages.SearchCustomEmoji <pyrogram.raw.functions.messages.SearchCustomEmoji>`
"""
