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
MessageMedia = Union[raw.types.MessageMediaContact, raw.types.MessageMediaDice, raw.types.MessageMediaDocument, raw.types.MessageMediaEmpty, raw.types.MessageMediaGame, raw.types.MessageMediaGeo, raw.types.MessageMediaGeoLive, raw.types.MessageMediaGiveaway, raw.types.MessageMediaGiveawayResults, raw.types.MessageMediaInvoice, raw.types.MessageMediaPaidMedia, raw.types.MessageMediaPhoto, raw.types.MessageMediaPoll, raw.types.MessageMediaStory, raw.types.MessageMediaToDo, raw.types.MessageMediaUnsupported, raw.types.MessageMediaVenue, raw.types.MessageMediaWebPage]
MessageMedia.__doc__ = """
    This base type has 18 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageMediaContact <pyrogram.raw.types.MessageMediaContact>`
            - :obj:`MessageMediaDice <pyrogram.raw.types.MessageMediaDice>`
            - :obj:`MessageMediaDocument <pyrogram.raw.types.MessageMediaDocument>`
            - :obj:`MessageMediaEmpty <pyrogram.raw.types.MessageMediaEmpty>`
            - :obj:`MessageMediaGame <pyrogram.raw.types.MessageMediaGame>`
            - :obj:`MessageMediaGeo <pyrogram.raw.types.MessageMediaGeo>`
            - :obj:`MessageMediaGeoLive <pyrogram.raw.types.MessageMediaGeoLive>`
            - :obj:`MessageMediaGiveaway <pyrogram.raw.types.MessageMediaGiveaway>`
            - :obj:`MessageMediaGiveawayResults <pyrogram.raw.types.MessageMediaGiveawayResults>`
            - :obj:`MessageMediaInvoice <pyrogram.raw.types.MessageMediaInvoice>`
            - :obj:`MessageMediaPaidMedia <pyrogram.raw.types.MessageMediaPaidMedia>`
            - :obj:`MessageMediaPhoto <pyrogram.raw.types.MessageMediaPhoto>`
            - :obj:`MessageMediaPoll <pyrogram.raw.types.MessageMediaPoll>`
            - :obj:`MessageMediaStory <pyrogram.raw.types.MessageMediaStory>`
            - :obj:`MessageMediaToDo <pyrogram.raw.types.MessageMediaToDo>`
            - :obj:`MessageMediaUnsupported <pyrogram.raw.types.MessageMediaUnsupported>`
            - :obj:`MessageMediaVenue <pyrogram.raw.types.MessageMediaVenue>`
            - :obj:`MessageMediaWebPage <pyrogram.raw.types.MessageMediaWebPage>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.UploadMedia <pyrogram.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyrogram.raw.functions.messages.UploadImportedMedia>`
"""
