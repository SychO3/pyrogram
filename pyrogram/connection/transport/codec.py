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

"""Pure-data frame codecs for MTProto transport protocols.

Each codec handles encoding/decoding of MTProto frames at the transport
layer. These are pure data transformations with no I/O — they operate on
bytearrays and return bytes.

Codec.decode() returns None when the buffer doesn't have enough data yet,
or a (payload, quick_ack_token) tuple. quick_ack_token is None for normal
frames and bytes for quick-ack frames.
"""

import os
from abc import ABC, abstractmethod
from binascii import crc32
from struct import pack, unpack
from typing import Optional, Tuple


class FrameCodec(ABC):
    """Base class for transport-layer frame codecs."""

    MARKER: Optional[bytes] = None

    @abstractmethod
    def encode(self, data: bytes, request_ack: bool = False) -> bytes:
        ...

    @abstractmethod
    def decode(self, buffer: bytearray) -> Optional[Tuple[Optional[bytes], Optional[bytes]]]:
        """Try to decode one frame from buffer.

        Consumes bytes from the front of buffer on success.

        Returns:
            None: not enough data yet
            (payload, None): normal data frame
            (None, ack_token): quick-ack frame (caller should continue reading)
        """
        ...


class AbridgedCodec(FrameCodec):
    """1-byte or 4-byte length header. Marker: 0xef."""

    MARKER = b"\xef"

    def encode(self, data: bytes, request_ack: bool = False) -> bytes:
        length = len(data) // 4

        if length <= 126:
            header = bytes([length | 0x80]) if request_ack else bytes([length])
        else:
            header = (b"\xff" if request_ack else b"\x7f") + length.to_bytes(3, "little")

        return header + data

    def decode(self, buffer: bytearray) -> Optional[Tuple[Optional[bytes], Optional[bytes]]]:
        if len(buffer) < 1:
            return None

        first = buffer[0]

        # Quick ACK: high bit set in first byte
        if first & 0x80:
            if len(buffer) < 4:
                return None
            token = bytes(reversed(buffer[:4]))
            del buffer[:4]
            return (None, token)

        # Extended length
        if first == 0x7F:
            if len(buffer) < 4:
                return None
            length = int.from_bytes(buffer[1:4], "little") * 4
            header_len = 4
        else:
            length = first * 4
            header_len = 1

        total = header_len + length
        if len(buffer) < total:
            return None

        payload = bytes(buffer[header_len:total])
        del buffer[:total]
        return (payload, None)


class IntermediateCodec(FrameCodec):
    """4-byte little-endian length header. Marker: 0xeeeeeeee."""

    MARKER = b"\xee" * 4

    def encode(self, data: bytes, request_ack: bool = False) -> bytes:
        length = len(data)
        if request_ack:
            length |= 0x80000000
        return pack("<I", length) + data

    def decode(self, buffer: bytearray) -> Optional[Tuple[Optional[bytes], Optional[bytes]]]:
        if len(buffer) < 4:
            return None

        value = unpack("<I", buffer[:4])[0]

        # Quick ACK: high bit set
        if value >= 0x80000000:
            token = bytes(buffer[:4])
            del buffer[:4]
            return (None, token)

        total = 4 + value
        if len(buffer) < total:
            return None

        payload = bytes(buffer[4:total])
        del buffer[:total]
        return (payload, None)


class PaddedIntermediateCodec(FrameCodec):
    """4-byte LE length + 0-15 bytes random padding. Marker: 0xdddddddd.

    Always used with obfuscation. The length field includes the padding.
    """

    MARKER = b"\xdd" * 4

    def encode(self, data: bytes, request_ack: bool = False) -> bytes:
        padding = os.urandom(os.urandom(1)[0] % 16)
        total_len = len(data) + len(padding)
        if request_ack:
            total_len |= 0x80000000
        return pack("<I", total_len) + data + padding

    def decode(self, buffer: bytearray) -> Optional[Tuple[Optional[bytes], Optional[bytes]]]:
        if len(buffer) < 4:
            return None

        tlen = unpack("<I", buffer[:4])[0]

        total = 4 + tlen
        if len(buffer) < total:
            return None

        data = bytes(buffer[4:total])
        del buffer[:total]

        # Quick ACK: 0xFFFFFFFF(4) + token(4) + optional padding
        if tlen <= 16 and len(data) >= 8 and data[:4] == b"\xff\xff\xff\xff":
            return (None, data[4:8])

        # Transport errors (< minimum MTProto payload of 24 bytes)
        if tlen < 24:
            return (data[:4], None)

        # Strip random transport padding: MTProto payload is always 8 (mod 16)
        padding_len = (tlen - 8) % 16
        payload_len = tlen - padding_len
        return (data[:payload_len], None)


class FullCodec(FrameCodec):
    """length(4) + seqno(4) + payload + CRC32(4). No marker, no obfuscation."""

    MARKER = None

    def __init__(self):
        self._send_seq_no = 0
        self._recv_seq_no = 0

    def encode(self, data: bytes, request_ack: bool = False) -> bytes:
        # request_ack is not supported by Full transport
        frame = pack("<II", len(data) + 12, self._send_seq_no) + data
        frame += pack("<I", crc32(frame))
        self._send_seq_no += 1
        return frame

    def decode(self, buffer: bytearray) -> Optional[Tuple[Optional[bytes], Optional[bytes]]]:
        if len(buffer) < 4:
            return None

        total_len = unpack("<I", buffer[:4])[0]
        if total_len < 12:
            # Invalid frame, consume and discard 4 bytes
            del buffer[:4]
            return (None, None)

        if len(buffer) < total_len:
            return None

        frame = bytes(buffer[:total_len])
        checksum = unpack("<I", frame[-4:])[0]

        if crc32(frame[:-4]) != checksum:
            # CRC mismatch, drop frame
            del buffer[:total_len]
            return (None, None)

        del buffer[:total_len]
        # Skip length(4) + seqno(4), strip CRC(4)
        payload = frame[8:-4]
        self._recv_seq_no += 1
        return (payload, None)
