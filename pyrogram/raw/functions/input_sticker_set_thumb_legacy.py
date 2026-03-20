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

from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Any

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject

if TYPE_CHECKING:
    from pyrogram import raw

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class InputStickerSetThumbLegacy(TLObject["raw.base.InputFileLocation"]):
    """Telegram API method.

    Details:
        - Layer: ``223``
        - ID: ``DBAEAE9``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyrogram.raw.base.InputStickerSet>`
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``

    Returns:
        :obj:`InputFileLocation <pyrogram.raw.base.InputFileLocation>`
    """

    __slots__: List[str] = ["stickerset", "volume_id", "local_id"]

    ID = 0xdbaeae9
    QUALNAME = "functions.InputStickerSetThumbLegacy"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", volume_id: int, local_id: int) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputStickerSetThumbLegacy":
        # No flags
        
        stickerset = TLObject.read(b)
        
        volume_id = Long.read(b)
        
        local_id = Int.read(b)
        
        return InputStickerSetThumbLegacy(stickerset=stickerset, volume_id=volume_id, local_id=local_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.stickerset.write())
        
        b.write(Long(self.volume_id))
        
        b.write(Int(self.local_id))
        
        return b.getvalue()
