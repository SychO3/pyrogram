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

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class StarGiftUnique(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``214``
        - ID: ``1BEFE865``

    Parameters:
        id: ``int`` ``64-bit``
        gift_id: ``int`` ``64-bit``
        title: ``str``
        slug: ``str``
        num: ``int`` ``32-bit``
        attributes: List of :obj:`StarGiftAttribute <pyrogram.raw.base.StarGiftAttribute>`
        availability_issued: ``int`` ``32-bit``
        availability_total: ``int`` ``32-bit``
        require_premium (optional): ``bool``
        resale_ton_only (optional): ``bool``
        theme_available (optional): ``bool``
        owner_id (optional): :obj:`Peer <pyrogram.raw.base.Peer>`
        owner_name (optional): ``str``
        owner_address (optional): ``str``
        gift_address (optional): ``str``
        resell_amount (optional): List of :obj:`StarsAmount <pyrogram.raw.base.StarsAmount>`
        released_by (optional): :obj:`Peer <pyrogram.raw.base.Peer>`
        value_amount (optional): ``int`` ``64-bit``
        value_currency (optional): ``str``
        theme_peer (optional): :obj:`Peer <pyrogram.raw.base.Peer>`

    Returns:
        :obj:`StarGift <pyrogram.raw.base.StarGift>`
    """

    __slots__: List[str] = ["id", "gift_id", "title", "slug", "num", "attributes", "availability_issued", "availability_total", "require_premium", "resale_ton_only", "theme_available", "owner_id", "owner_name", "owner_address", "gift_address", "resell_amount", "released_by", "value_amount", "value_currency", "theme_peer"]

    ID = 0x1befe865
    QUALNAME = "functions.StarGiftUnique"

    def __init__(self, *, id: int, gift_id: int, title: str, slug: str, num: int, attributes: List["raw.base.StarGiftAttribute"], availability_issued: int, availability_total: int, require_premium: Optional[bool] = None, resale_ton_only: Optional[bool] = None, theme_available: Optional[bool] = None, owner_id: "raw.base.Peer" = None, owner_name: Optional[str] = None, owner_address: Optional[str] = None, gift_address: Optional[str] = None, resell_amount: Optional[List["raw.base.StarsAmount"]] = None, released_by: "raw.base.Peer" = None, value_amount: Optional[int] = None, value_currency: Optional[str] = None, theme_peer: "raw.base.Peer" = None) -> None:
        self.id = id  # long
        self.gift_id = gift_id  # long
        self.title = title  # string
        self.slug = slug  # string
        self.num = num  # int
        self.attributes = attributes  # Vector<StarGiftAttribute>
        self.availability_issued = availability_issued  # int
        self.availability_total = availability_total  # int
        self.require_premium = require_premium  # flags.6?true
        self.resale_ton_only = resale_ton_only  # flags.7?true
        self.theme_available = theme_available  # flags.9?true
        self.owner_id = owner_id  # flags.0?Peer
        self.owner_name = owner_name  # flags.1?string
        self.owner_address = owner_address  # flags.2?string
        self.gift_address = gift_address  # flags.3?string
        self.resell_amount = resell_amount  # flags.4?Vector<StarsAmount>
        self.released_by = released_by  # flags.5?Peer
        self.value_amount = value_amount  # flags.8?long
        self.value_currency = value_currency  # flags.8?string
        self.theme_peer = theme_peer  # flags.10?Peer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGiftUnique":
        
        flags = Int.read(b)
        
        require_premium = True if flags & (1 << 6) else False
        resale_ton_only = True if flags & (1 << 7) else False
        theme_available = True if flags & (1 << 9) else False
        id = Long.read(b)
        
        gift_id = Long.read(b)
        
        title = String.read(b)
        
        slug = String.read(b)
        
        num = Int.read(b)
        
        owner_id = TLObject.read(b) if flags & (1 << 0) else None
        
        owner_name = String.read(b) if flags & (1 << 1) else None
        owner_address = String.read(b) if flags & (1 << 2) else None
        attributes = TLObject.read(b)
        
        availability_issued = Int.read(b)
        
        availability_total = Int.read(b)
        
        gift_address = String.read(b) if flags & (1 << 3) else None
        resell_amount = TLObject.read(b) if flags & (1 << 4) else []
        
        released_by = TLObject.read(b) if flags & (1 << 5) else None
        
        value_amount = Long.read(b) if flags & (1 << 8) else None
        value_currency = String.read(b) if flags & (1 << 8) else None
        theme_peer = TLObject.read(b) if flags & (1 << 10) else None
        
        return StarGiftUnique(id=id, gift_id=gift_id, title=title, slug=slug, num=num, attributes=attributes, availability_issued=availability_issued, availability_total=availability_total, require_premium=require_premium, resale_ton_only=resale_ton_only, theme_available=theme_available, owner_id=owner_id, owner_name=owner_name, owner_address=owner_address, gift_address=gift_address, resell_amount=resell_amount, released_by=released_by, value_amount=value_amount, value_currency=value_currency, theme_peer=theme_peer)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 6) if self.require_premium else 0
        flags |= (1 << 7) if self.resale_ton_only else 0
        flags |= (1 << 9) if self.theme_available else 0
        flags |= (1 << 0) if self.owner_id is not None else 0
        flags |= (1 << 1) if self.owner_name is not None else 0
        flags |= (1 << 2) if self.owner_address is not None else 0
        flags |= (1 << 3) if self.gift_address is not None else 0
        flags |= (1 << 4) if self.resell_amount else 0
        flags |= (1 << 5) if self.released_by is not None else 0
        flags |= (1 << 8) if self.value_amount is not None else 0
        flags |= (1 << 8) if self.value_currency is not None else 0
        flags |= (1 << 10) if self.theme_peer is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.id))
        
        b.write(Long(self.gift_id))
        
        b.write(String(self.title))
        
        b.write(String(self.slug))
        
        b.write(Int(self.num))
        
        if self.owner_id is not None:
            b.write(self.owner_id.write())
        
        if self.owner_name is not None:
            b.write(String(self.owner_name))
        
        if self.owner_address is not None:
            b.write(String(self.owner_address))
        
        b.write(Vector(self.attributes))
        
        b.write(Int(self.availability_issued))
        
        b.write(Int(self.availability_total))
        
        if self.gift_address is not None:
            b.write(String(self.gift_address))
        
        if self.resell_amount is not None:
            b.write(Vector(self.resell_amount))
        
        if self.released_by is not None:
            b.write(self.released_by.write())
        
        if self.value_amount is not None:
            b.write(Long(self.value_amount))
        
        if self.value_currency is not None:
            b.write(String(self.value_currency))
        
        if self.theme_peer is not None:
            b.write(self.theme_peer.write())
        
        return b.getvalue()
