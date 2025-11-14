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


class Boost(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.Boost`.

    Details:
        - Layer: ``216``
        - ID: ``4B3E14D6``

    Parameters:
        id: ``str``
        date: ``int`` ``32-bit``
        expires: ``int`` ``32-bit``
        gift (optional): ``bool``
        giveaway (optional): ``bool``
        unclaimed (optional): ``bool``
        user_id (optional): ``int`` ``64-bit``
        giveaway_msg_id (optional): ``int`` ``32-bit``
        used_gift_slug (optional): ``str``
        multiplier (optional): ``int`` ``32-bit``
        stars (optional): ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "date", "expires", "gift", "giveaway", "unclaimed", "user_id", "giveaway_msg_id", "used_gift_slug", "multiplier", "stars"]

    ID = 0x4b3e14d6
    QUALNAME = "types.Boost"

    def __init__(self, *, id: str, date: int, expires: int, gift: Optional[bool] = None, giveaway: Optional[bool] = None, unclaimed: Optional[bool] = None, user_id: Optional[int] = None, giveaway_msg_id: Optional[int] = None, used_gift_slug: Optional[str] = None, multiplier: Optional[int] = None, stars: Optional[int] = None) -> None:
        self.id = id  # string
        self.date = date  # int
        self.expires = expires  # int
        self.gift = gift  # flags.1?true
        self.giveaway = giveaway  # flags.2?true
        self.unclaimed = unclaimed  # flags.3?true
        self.user_id = user_id  # flags.0?long
        self.giveaway_msg_id = giveaway_msg_id  # flags.2?int
        self.used_gift_slug = used_gift_slug  # flags.4?string
        self.multiplier = multiplier  # flags.5?int
        self.stars = stars  # flags.6?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "Boost":
        
        flags = Int.read(b)
        
        gift = True if flags & (1 << 1) else False
        giveaway = True if flags & (1 << 2) else False
        unclaimed = True if flags & (1 << 3) else False
        id = String.read(b)
        
        user_id = Long.read(b) if flags & (1 << 0) else None
        giveaway_msg_id = Int.read(b) if flags & (1 << 2) else None
        date = Int.read(b)
        
        expires = Int.read(b)
        
        used_gift_slug = String.read(b) if flags & (1 << 4) else None
        multiplier = Int.read(b) if flags & (1 << 5) else None
        stars = Long.read(b) if flags & (1 << 6) else None
        return Boost(id=id, date=date, expires=expires, gift=gift, giveaway=giveaway, unclaimed=unclaimed, user_id=user_id, giveaway_msg_id=giveaway_msg_id, used_gift_slug=used_gift_slug, multiplier=multiplier, stars=stars)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.gift else 0
        flags |= (1 << 2) if self.giveaway else 0
        flags |= (1 << 3) if self.unclaimed else 0
        flags |= (1 << 0) if self.user_id is not None else 0
        flags |= (1 << 2) if self.giveaway_msg_id is not None else 0
        flags |= (1 << 4) if self.used_gift_slug is not None else 0
        flags |= (1 << 5) if self.multiplier is not None else 0
        flags |= (1 << 6) if self.stars is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.id))
        
        if self.user_id is not None:
            b.write(Long(self.user_id))
        
        if self.giveaway_msg_id is not None:
            b.write(Int(self.giveaway_msg_id))
        
        b.write(Int(self.date))
        
        b.write(Int(self.expires))
        
        if self.used_gift_slug is not None:
            b.write(String(self.used_gift_slug))
        
        if self.multiplier is not None:
            b.write(Int(self.multiplier))
        
        if self.stars is not None:
            b.write(Long(self.stars))
        
        return b.getvalue()
