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
ProfileTab = Union[raw.types.ProfileTabFiles, raw.types.ProfileTabGifs, raw.types.ProfileTabGifts, raw.types.ProfileTabLinks, raw.types.ProfileTabMedia, raw.types.ProfileTabMusic, raw.types.ProfileTabPosts, raw.types.ProfileTabVoice]
ProfileTab.__doc__ = """
    This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ProfileTabFiles <pyrogram.raw.types.ProfileTabFiles>`
            - :obj:`ProfileTabGifs <pyrogram.raw.types.ProfileTabGifs>`
            - :obj:`ProfileTabGifts <pyrogram.raw.types.ProfileTabGifts>`
            - :obj:`ProfileTabLinks <pyrogram.raw.types.ProfileTabLinks>`
            - :obj:`ProfileTabMedia <pyrogram.raw.types.ProfileTabMedia>`
            - :obj:`ProfileTabMusic <pyrogram.raw.types.ProfileTabMusic>`
            - :obj:`ProfileTabPosts <pyrogram.raw.types.ProfileTabPosts>`
            - :obj:`ProfileTabVoice <pyrogram.raw.types.ProfileTabVoice>`
"""
