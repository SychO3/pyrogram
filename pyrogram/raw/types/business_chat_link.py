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


class BusinessChatLink(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.BusinessChatLink`.

    Details:
        - Layer: ``216``
        - ID: ``B4AE666F``

    Parameters:
        link: ``str``
        message: ``str``
        views: ``int`` ``32-bit``
        entities (optional): List of :obj:`MessageEntity <pyrogram.raw.base.MessageEntity>`
        title (optional): ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.CreateBusinessChatLink <pyrogram.raw.functions.account.CreateBusinessChatLink>`
            - :obj:`account.EditBusinessChatLink <pyrogram.raw.functions.account.EditBusinessChatLink>`
    """

    __slots__: List[str] = ["link", "message", "views", "entities", "title"]

    ID = 0xb4ae666f
    QUALNAME = "types.BusinessChatLink"

    def __init__(self, *, link: str, message: str, views: int, entities: Optional[List["raw.base.MessageEntity"]] = None, title: Optional[str] = None) -> None:
        self.link = link  # string
        self.message = message  # string
        self.views = views  # int
        self.entities = entities  # flags.0?Vector<MessageEntity>
        self.title = title  # flags.1?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BusinessChatLink":
        
        flags = Int.read(b)
        
        link = String.read(b)
        
        message = String.read(b)
        
        entities = TLObject.read(b) if flags & (1 << 0) else []
        
        title = String.read(b) if flags & (1 << 1) else None
        views = Int.read(b)
        
        return BusinessChatLink(link=link, message=message, views=views, entities=entities, title=title)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.entities else 0
        flags |= (1 << 1) if self.title is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.link))
        
        b.write(String(self.message))
        
        if self.entities is not None:
            b.write(Vector(self.entities))
        
        if self.title is not None:
            b.write(String(self.title))
        
        b.write(Int(self.views))
        
        return b.getvalue()
