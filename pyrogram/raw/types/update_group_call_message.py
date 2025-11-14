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


class UpdateGroupCallMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``216``
        - ID: ``78C314E0``

    Parameters:
        call: :obj:`InputGroupCall <pyrogram.raw.base.InputGroupCall>`
        from_id: :obj:`Peer <pyrogram.raw.base.Peer>`
        random_id: ``int`` ``64-bit``
        message: :obj:`TextWithEntities <pyrogram.raw.base.TextWithEntities>`
    """

    __slots__: List[str] = ["call", "from_id", "random_id", "message"]

    ID = 0x78c314e0
    QUALNAME = "types.UpdateGroupCallMessage"

    def __init__(self, *, call: "raw.base.InputGroupCall", from_id: "raw.base.Peer", random_id: int, message: "raw.base.TextWithEntities") -> None:
        self.call = call  # InputGroupCall
        self.from_id = from_id  # Peer
        self.random_id = random_id  # long
        self.message = message  # TextWithEntities

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateGroupCallMessage":
        # No flags
        
        call = TLObject.read(b)
        
        from_id = TLObject.read(b)
        
        random_id = Long.read(b)
        
        message = TLObject.read(b)
        
        return UpdateGroupCallMessage(call=call, from_id=from_id, random_id=random_id, message=message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(self.from_id.write())
        
        b.write(Long(self.random_id))
        
        b.write(self.message.write())
        
        return b.getvalue()
