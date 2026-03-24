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
import logging
from struct import pack, unpack
from typing import Optional, Tuple, Union

from .tcp import TCP, ProxyDict

log = logging.getLogger(__name__)


class TCPIntermediate(TCP):
    def __init__(
        self,
        ipv6: bool,
        proxy: Union[str, ProxyDict, None] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop)

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)
        await super().send(b"\xee" * 4, wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args, request_ack: bool = False) -> None:
        length = len(data)
        if request_ack:
            length |= 0x80000000
        await super().send(pack("<I", length) + data)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        while True:
            raw_length = await super().recv(4)

            if raw_length is None:
                return None

            value = unpack("<I", raw_length)[0]

            if value >= 0x80000000:
                if self.quick_ack_handler:
                    self.quick_ack_handler(raw_length)
                continue

            return await super().recv(value)
