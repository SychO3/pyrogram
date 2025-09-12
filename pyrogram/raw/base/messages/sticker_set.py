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
StickerSet = Union[raw.types.messages.StickerSet, raw.types.messages.StickerSetNotModified]
StickerSet.__doc__ = """
    This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.StickerSet <pyrogram.raw.types.messages.StickerSet>`
            - :obj:`messages.StickerSetNotModified <pyrogram.raw.types.messages.StickerSetNotModified>`

    See Also:
        This object can be returned by 9 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickerSet <pyrogram.raw.functions.messages.GetStickerSet>`
            - :obj:`stickers.CreateStickerSet <pyrogram.raw.functions.stickers.CreateStickerSet>`
            - :obj:`stickers.RemoveStickerFromSet <pyrogram.raw.functions.stickers.RemoveStickerFromSet>`
            - :obj:`stickers.ChangeStickerPosition <pyrogram.raw.functions.stickers.ChangeStickerPosition>`
            - :obj:`stickers.AddStickerToSet <pyrogram.raw.functions.stickers.AddStickerToSet>`
            - :obj:`stickers.SetStickerSetThumb <pyrogram.raw.functions.stickers.SetStickerSetThumb>`
            - :obj:`stickers.ChangeSticker <pyrogram.raw.functions.stickers.ChangeSticker>`
            - :obj:`stickers.RenameStickerSet <pyrogram.raw.functions.stickers.RenameStickerSet>`
            - :obj:`stickers.ReplaceSticker <pyrogram.raw.functions.stickers.ReplaceSticker>`
"""
