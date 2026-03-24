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

import asyncio
import time

import pyrogram
from pyrogram.raw.core import Message, MsgContainer, TLObject
from pyrogram.raw.functions import Ping
from pyrogram.raw.types import HttpWait, MsgsAck


class MsgFactory:
    def __init__(self, client: "pyrogram.Client"):
        self.client = client

        self._last_msg_id = 0
        self._lock = asyncio.Lock()
        self._content_related_messages_sent = 0

    async def allocate_message_identity(self) -> int:
        async with self._lock:
            base_msg_id = int(self.client.server_time * (2**32)) & ~0b11

            if base_msg_id <= self._last_msg_id:
                base_msg_id = self._last_msg_id + 4

            self._last_msg_id = base_msg_id

            return base_msg_id

    async def create(self, body: TLObject) -> Message:
        async with self._lock:
            base_msg_id = int(self.client.server_time * (2**32)) & ~0b11

            if base_msg_id <= self._last_msg_id:
                base_msg_id = self._last_msg_id + 4

            self._last_msg_id = base_msg_id

            is_content_related = not isinstance(body, (Ping, HttpWait, MsgsAck, MsgContainer))
            seq_no = (self._content_related_messages_sent * 2) + (1 if is_content_related else 0)

            if is_content_related:
                self._content_related_messages_sent += 1

            return Message(body, base_msg_id, seq_no, len(body))
