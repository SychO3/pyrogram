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

"""MTProto obfuscation layer (AES-256-CTR).

Extracts the nonce generation + encrypt/decrypt logic that was duplicated
across TCPAbridgedO, TCPIntermediateO, and TCPPaddedIntermediateO into a
single reusable component.

The AES-CTR state (iv: bytearray, state: bytearray(1)) is mutable and
advances across calls — this is by design; each encrypt/decrypt call
continues where the last one left off.
"""

import os
from typing import Optional, Tuple

from pyrogram.crypto import aes

RESERVED = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xee" * 4, b"\xdd" * 4)


class ObfuscationLayer:
    """AES-256-CTR obfuscation for MTProto transports.

    Args:
        protocol_marker: The 4-byte marker to embed at nonce[56:60].
            0xEFEFEFEF for abridged, 0xEEEEEEEE for intermediate,
            0xDDDDDDDD for padded intermediate.
    """

    def __init__(self, protocol_marker: bytes):
        if len(protocol_marker) != 4:
            raise ValueError("protocol_marker must be exactly 4 bytes")
        self._marker = protocol_marker
        self._encrypt: Optional[Tuple[bytes, bytearray, bytearray]] = None
        self._decrypt: Optional[Tuple[bytes, bytearray, bytearray]] = None
        self._nonce: Optional[bytes] = None

    def generate_nonce(self) -> bytes:
        """Generate 64-byte nonce with embedded protocol marker.

        Derives encrypt/decrypt keys from the nonce. The returned nonce
        has bytes [56:64] encrypted with the encrypt key (the server
        needs this to derive its own keys).

        Returns:
            64-byte nonce ready to send to the server.
        """
        while True:
            nonce = bytearray(os.urandom(64))

            if (
                bytes([nonce[0]]) != b"\xef"
                and nonce[:4] not in RESERVED
                and nonce[4:8] != b"\x00" * 4
            ):
                # Embed the protocol marker at bytes 56-59
                nonce[56] = self._marker[0]
                nonce[57] = self._marker[1]
                nonce[58] = self._marker[2]
                nonce[59] = self._marker[3]
                break

        # Derive keys: encrypt from nonce[8:56], decrypt from reversed
        temp = bytearray(nonce[55:7:-1])

        self._encrypt = (bytes(nonce[8:40]), bytearray(nonce[40:56]), bytearray(1))
        self._decrypt = (bytes(temp[0:32]), bytearray(temp[32:48]), bytearray(1))

        # Encrypt bytes [56:64] of the nonce so the server can derive keys
        nonce[56:64] = aes.ctr256_encrypt(bytes(nonce), *self._encrypt)[56:64]

        self._nonce = bytes(nonce)
        return self._nonce

    def encrypt(self, data: bytes) -> bytes:
        if self._encrypt is None:
            raise RuntimeError("generate_nonce() must be called before encrypt()")
        return aes.ctr256_encrypt(data, *self._encrypt)

    def decrypt(self, data: bytes) -> bytes:
        if self._decrypt is None:
            raise RuntimeError("generate_nonce() must be called before decrypt()")
        return aes.ctr256_decrypt(data, *self._decrypt)
