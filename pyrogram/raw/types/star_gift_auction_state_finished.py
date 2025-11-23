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


class StarGiftAuctionStateFinished(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.StarGiftAuctionState`.

    Details:
        - Layer: ``218``
        - ID: ``7D967C3A``

    Parameters:
        start_date: ``int`` ``32-bit``
        end_date: ``int`` ``32-bit``
        average_price: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["start_date", "end_date", "average_price"]

    ID = 0x7d967c3a
    QUALNAME = "types.StarGiftAuctionStateFinished"

    def __init__(self, *, start_date: int, end_date: int, average_price: int) -> None:
        self.start_date = start_date  # int
        self.end_date = end_date  # int
        self.average_price = average_price  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGiftAuctionStateFinished":
        # No flags
        
        start_date = Int.read(b)
        
        end_date = Int.read(b)
        
        average_price = Long.read(b)
        
        return StarGiftAuctionStateFinished(start_date=start_date, end_date=end_date, average_price=average_price)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.start_date))
        
        b.write(Int(self.end_date))
        
        b.write(Long(self.average_price))
        
        return b.getvalue()
