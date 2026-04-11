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
from struct import pack, unpack
from typing import Optional, Tuple, Union

from pyrogram.crypto import aes

from .ws import WS

log = logging.getLogger(__name__)


class WSPaddedIntermediateO(WS):
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
                nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xDD
                break

        temp = bytearray(nonce[55:7:-1])

        self.encrypt = (nonce[8:40], nonce[40:56], bytearray(1))
        self.decrypt = (temp[0:32], temp[32:48], bytearray(1))

        nonce[56:64] = aes.ctr256_encrypt(nonce, *self.encrypt)[56:64]

        await super().send(nonce, wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args, request_ack: bool = False) -> None:
        padding = os.urandom(os.urandom(1)[0] % 16)
        total_len = len(data) + len(padding)
        if request_ack:
            total_len |= 0x80000000
        data_padded = pack("<I", total_len) + data + padding
        payload = await asyncio.get_event_loop().run_in_executor(
            self.crypto_executor, aes.ctr256_encrypt, data_padded, *self.encrypt
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

            if len(data) < 4:
                return None

            tlen = unpack("<I", data[:4])[0]
            payload = data[4:]

            # Quick ACK: 0xFFFFFFFF(4) + token(4) + padding(0-8)
            if tlen <= 16 and len(payload) >= 8 and payload[:4] == b"\xff\xff\xff\xff":
                if self.quick_ack_handler:
                    self.quick_ack_handler(bytes(payload[4:8]))
                continue

            # Transport errors (< minimum MTProto payload of 24 bytes)
            if tlen < 24:
                return bytes(payload[:4])

            # Strip random transport padding
            # Normal MTProto payload is always congruent to 8 mod 16: 24 + N*16
            padding_len = (tlen - 8) % 16
            payload_len = tlen - padding_len
            return bytes(payload[:payload_len])
