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


class MessagesSlice(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.messages.Messages`.

    Details:
        - Layer: ``216``
        - ID: ``5F206716``

    Parameters:
        count: ``int`` ``32-bit``
        messages: List of :obj:`Message <pyrogram.raw.base.Message>`
        topics: List of :obj:`ForumTopic <pyrogram.raw.base.ForumTopic>`
        chats: List of :obj:`Chat <pyrogram.raw.base.Chat>`
        users: List of :obj:`User <pyrogram.raw.base.User>`
        inexact (optional): ``bool``
        next_rate (optional): ``int`` ``32-bit``
        offset_id_offset (optional): ``int`` ``32-bit``
        search_flood (optional): :obj:`SearchPostsFlood <pyrogram.raw.base.SearchPostsFlood>`

    See Also:
        This object can be returned by 15 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <pyrogram.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <pyrogram.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <pyrogram.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <pyrogram.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.GetUnreadMentions <pyrogram.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <pyrogram.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <pyrogram.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <pyrogram.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <pyrogram.raw.functions.messages.GetReplies>`
            - :obj:`messages.GetUnreadReactions <pyrogram.raw.functions.messages.GetUnreadReactions>`
            - :obj:`messages.SearchSentMedia <pyrogram.raw.functions.messages.SearchSentMedia>`
            - :obj:`messages.GetSavedHistory <pyrogram.raw.functions.messages.GetSavedHistory>`
            - :obj:`messages.GetQuickReplyMessages <pyrogram.raw.functions.messages.GetQuickReplyMessages>`
            - :obj:`channels.GetMessages <pyrogram.raw.functions.channels.GetMessages>`
            - :obj:`channels.SearchPosts <pyrogram.raw.functions.channels.SearchPosts>`
    """

    __slots__: List[str] = ["count", "messages", "topics", "chats", "users", "inexact", "next_rate", "offset_id_offset", "search_flood"]

    ID = 0x5f206716
    QUALNAME = "types.messages.MessagesSlice"

    def __init__(self, *, count: int, messages: List["raw.base.Message"], topics: List["raw.base.ForumTopic"], chats: List["raw.base.Chat"], users: List["raw.base.User"], inexact: Optional[bool] = None, next_rate: Optional[int] = None, offset_id_offset: Optional[int] = None, search_flood: "raw.base.SearchPostsFlood" = None) -> None:
        self.count = count  # int
        self.messages = messages  # Vector<Message>
        self.topics = topics  # Vector<ForumTopic>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.inexact = inexact  # flags.1?true
        self.next_rate = next_rate  # flags.0?int
        self.offset_id_offset = offset_id_offset  # flags.2?int
        self.search_flood = search_flood  # flags.3?SearchPostsFlood

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessagesSlice":
        
        flags = Int.read(b)
        
        inexact = True if flags & (1 << 1) else False
        count = Int.read(b)
        
        next_rate = Int.read(b) if flags & (1 << 0) else None
        offset_id_offset = Int.read(b) if flags & (1 << 2) else None
        search_flood = TLObject.read(b) if flags & (1 << 3) else None
        
        messages = TLObject.read(b)
        
        topics = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return MessagesSlice(count=count, messages=messages, topics=topics, chats=chats, users=users, inexact=inexact, next_rate=next_rate, offset_id_offset=offset_id_offset, search_flood=search_flood)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.inexact else 0
        flags |= (1 << 0) if self.next_rate is not None else 0
        flags |= (1 << 2) if self.offset_id_offset is not None else 0
        flags |= (1 << 3) if self.search_flood is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.count))
        
        if self.next_rate is not None:
            b.write(Int(self.next_rate))
        
        if self.offset_id_offset is not None:
            b.write(Int(self.offset_id_offset))
        
        if self.search_flood is not None:
            b.write(self.search_flood.write())
        
        b.write(Vector(self.messages))
        
        b.write(Vector(self.topics))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
