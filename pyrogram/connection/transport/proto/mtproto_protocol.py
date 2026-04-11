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

"""Event-driven asyncio.Protocol for MTProto frame reception."""

import asyncio
import logging
from typing import Optional

from pyrogram.connection.transport.codec import FrameCodec
from pyrogram.connection.transport.obfuscation import ObfuscationLayer

log = logging.getLogger(__name__)

# Backpressure: pause reading when queue reaches this size
HIGH_WATER = 128
LOW_WATER = 32


class MTProtoProtocol(asyncio.Protocol):
    """asyncio.Protocol that receives raw bytes, decrypts (if obfuscated),
    decodes frames via FrameCodec, and pushes them into an asyncio.Queue.

    Implements backpressure: pauses reading when the queue is full,
    resumes when it drains below the low-water mark.
    """

    def __init__(
        self,
        codec: FrameCodec,
        obfuscation: Optional[ObfuscationLayer],
        frame_queue: asyncio.Queue,
        ack_source: Optional[object] = None,
    ):
        self._codec = codec
        self._obfuscation = obfuscation
        self._queue = frame_queue
        self._ack_source = ack_source

        self._transport: Optional[asyncio.Transport] = None
        self._buffer = bytearray()
        self._paused = False

    @property
    def transport(self) -> Optional[asyncio.Transport]:
        return self._transport

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._transport = transport
        log.debug("Protocol connection established")

    def data_received(self, data: bytes) -> None:
        if self._obfuscation is not None:
            data = self._obfuscation.decrypt(data)

        self._buffer.extend(data)

        while True:
            result = self._codec.decode(self._buffer)
            if result is None:
                break

            payload, ack_token = result

            if ack_token is not None:
                handler = getattr(self._ack_source, 'quick_ack_handler', None)
                if handler is not None:
                    handler(ack_token)
                continue

            if payload is None:
                continue

            try:
                self._queue.put_nowait(payload)
            except asyncio.QueueFull:
                log.warning("Frame queue full, dropping frame (%d bytes)", len(payload))
                continue

            if not self._paused and self._queue.qsize() >= HIGH_WATER:
                self._paused = True
                if self._transport is not None:
                    self._transport.pause_reading()
                    log.debug("Paused reading (queue=%d)", self._queue.qsize())

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc is not None:
            log.debug("Protocol connection lost: %s", exc)
        else:
            log.debug("Protocol connection closed")

        # EOF sentinel
        try:
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass

        self._transport = None

    def eof_received(self) -> Optional[bool]:
        try:
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass
        return False

    def resume_if_needed(self) -> None:
        """Called by ProtoTransport after consuming from the queue."""
        if self._paused and self._queue.qsize() <= LOW_WATER:
            self._paused = False
            if self._transport is not None:
                self._transport.resume_reading()
                log.debug("Resumed reading (queue=%d)", self._queue.qsize())
