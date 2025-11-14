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


class SendGroupCallMessage(TLObject["raw.base.Bool"]):
    """Telegram API method.

    Details:
        - Layer: ``216``
        - ID: ``87893014``

    Parameters:
        call: :obj:`InputGroupCall <pyrogram.raw.base.InputGroupCall>`
        random_id: ``int`` ``64-bit``
        message: :obj:`TextWithEntities <pyrogram.raw.base.TextWithEntities>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["call", "random_id", "message"]

    ID = 0x87893014
    QUALNAME = "functions.phone.SendGroupCallMessage"

    def __init__(self, *, call: "raw.base.InputGroupCall", random_id: int, message: "raw.base.TextWithEntities") -> None:
        self.call = call  # InputGroupCall
        self.random_id = random_id  # long
        self.message = message  # TextWithEntities

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendGroupCallMessage":
        # No flags
        
        call = TLObject.read(b)
        
        random_id = Long.read(b)
        
        message = TLObject.read(b)
        
        return SendGroupCallMessage(call=call, random_id=random_id, message=message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Long(self.random_id))
        
        b.write(self.message.write())
        
        return b.getvalue()
