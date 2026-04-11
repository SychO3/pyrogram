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
import os
from typing import Optional, Tuple, Union

from pyrogram.crypto import aes

from .ws import WS

log = logging.getLogger(__name__)


class WSAbridgedO(WS):
    RESERVED = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xee" * 4, b"\xdd" * 4)

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Union[str, dict, None] = None,
        crypto_executor_workers: int = 1,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers)

        self.encrypt = None
        self.decrypt = None

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)

        while True:
            nonce = bytearray(os.urandom(64))

            if (
                bytes([nonce[0]]) != b"\xef"
                and nonce[:4] not in self.RESERVED
                and nonce[4:8] != b"\x00" * 4
            ):
                nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xEF
                break

        temp = bytearray(nonce[55:7:-1])

        self.encrypt = (nonce[8:40], nonce[40:56], bytearray(1))
        self.decrypt = (temp[0:32], temp[32:48], bytearray(1))

        nonce[56:64] = aes.ctr256_encrypt(nonce, *self.encrypt)[56:64]

        await super().send(nonce, wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args, request_ack: bool = False) -> None:
        length = len(data) // 4

        if length <= 126:
            header = bytes([length | 0x80]) if request_ack else bytes([length])
        else:
            header = (b"\xff" if request_ack else b"\x7f") + length.to_bytes(3, "little")

        payload = await asyncio.get_event_loop().run_in_executor(
            self.crypto_executor, aes.ctr256_encrypt, header + data, *self.encrypt
        )
        await super().send(payload)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        while True:
            data = await super().recv()

            if data is None:
                return None

            data = await asyncio.get_event_loop().run_in_executor(
                self.crypto_executor, aes.ctr256_decrypt, data, *self.decrypt
            )

            # Parse abridged framing from decrypted data
            if len(data) < 1:
                return None

            first = data[0]

            # Quick ACK: high bit set in first byte
            if first & 0x80:
                if len(data) >= 4 and self.quick_ack_handler:
                    token = bytes(reversed(data[:4]))
                    self.quick_ack_handler(token)
                continue

            if first == 0x7f:
                # Extended length: 3 bytes LE after 0x7f
                if len(data) < 4:
                    return None
                payload_length = int.from_bytes(data[1:4], "little") * 4
                return bytes(data[4:4 + payload_length])
            else:
                payload_length = first * 4
                return bytes(data[1:1 + payload_length])
