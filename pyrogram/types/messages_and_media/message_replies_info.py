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

from typing import List, Optional

from pyrogram import raw, utils

from ..object import Object


class MessageRepliesInfo(Object):
    """Contains information about message replies.

    Parameters:
        replies_count (``int``):
            Number of replies to the message.

        is_comments (``bool``, *optional*):
            True, if this is a comments thread associated with a channel post.

        recent_replier_ids (List of ``int``, *optional*):
            IDs of the last few users who replied to the message.

        channel_id (``int``, *optional*):
            ID of the discussion group (channel comments).

        max_id (``int``, *optional*):
            ID of the latest reply in this thread.

        read_max_id (``int``, *optional*):
            ID of the latest read reply in this thread.
    """

    def __init__(
        self, *,
        replies_count: int,
        is_comments: Optional[bool] = None,
        recent_replier_ids: Optional[List[int]] = None,
        channel_id: Optional[int] = None,
        max_id: Optional[int] = None,
        read_max_id: Optional[int] = None
    ):
        super().__init__()

        self.replies_count = replies_count
        self.is_comments = is_comments
        self.recent_replier_ids = recent_replier_ids
        self.channel_id = channel_id
        self.max_id = max_id
        self.read_max_id = read_max_id

    @staticmethod
    def _parse(replies: "raw.types.MessageReplies") -> Optional["MessageRepliesInfo"]:
        if not replies:
            return None

        return MessageRepliesInfo(
            replies_count=replies.replies,
            is_comments=replies.comments or None,
            recent_replier_ids=[
                utils.get_raw_peer_id(p)
                for p in (replies.recent_repliers or [])
            ] or None,
            channel_id=replies.channel_id,
            max_id=replies.max_id,
            read_max_id=replies.read_max_id
        )
