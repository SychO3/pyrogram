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


class ChatThemes(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``214``
        - ID: ``16484857``

    Parameters:
        hash: ``int`` ``64-bit``
        themes: List of :obj:`ChatTheme <pyrogram.raw.base.ChatTheme>`
        chats: List of :obj:`Chat <pyrogram.raw.base.Chat>`
        users: List of :obj:`User <pyrogram.raw.base.User>`
        next_offset (optional): ``int`` ``32-bit``

    Returns:
        :obj:`account.ChatThemes <pyrogram.raw.base.account.ChatThemes>`
    """

    __slots__: List[str] = ["hash", "themes", "chats", "users", "next_offset"]

    ID = 0x16484857
    QUALNAME = "functions.account.ChatThemes"

    def __init__(self, *, hash: int, themes: List["raw.base.ChatTheme"], chats: List["raw.base.Chat"], users: List["raw.base.User"], next_offset: Optional[int] = None) -> None:
        self.hash = hash  # long
        self.themes = themes  # Vector<ChatTheme>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.next_offset = next_offset  # flags.0?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatThemes":
        
        flags = Int.read(b)
        
        hash = Long.read(b)
        
        themes = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        next_offset = Int.read(b) if flags & (1 << 0) else None
        return ChatThemes(hash=hash, themes=themes, chats=chats, users=users, next_offset=next_offset)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.next_offset is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.themes))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        if self.next_offset is not None:
            b.write(Int(self.next_offset))
        
        return b.getvalue()
