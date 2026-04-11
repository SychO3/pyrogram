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

"""WebSocket MTProto transport using aiohttp."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, Union

import aiohttp

from pyrogram import utils
from pyrogram.connection.transport.base import TransportBase
from pyrogram.connection.transport.codec import (
    AbridgedCodec,
    FrameCodec,
    IntermediateCodec,
    PaddedIntermediateCodec,
)
from pyrogram.connection.transport.obfuscation import ObfuscationLayer

log = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10


class WSTransport(TransportBase):
    """WebSocket-based MTProto transport.

    MTProto spec requires obfuscation over WebSocket. The nonce is sent
    as the first binary message, then all subsequent messages are
    obfuscated frames.

    Requires aiohttp (optional dependency).
    """

    def __init__(
        self,
        codec: FrameCodec,
        obfuscation: ObfuscationLayer,
        ipv6: bool = False,
        proxy: Union[dict, str, None] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        crypto_executor: Optional[ThreadPoolExecutor] = None,
    ):
        self._codec = codec
        self._obfuscation = obfuscation
        self.ipv6 = ipv6
        self.proxy = proxy

        if crypto_executor is not None:
            self.crypto_executor = crypto_executor
            self._owns_crypto_executor = False
        else:
            self.crypto_executor = ThreadPoolExecutor(
                max_workers=crypto_executor_workers,
                thread_name_prefix="CryptoWorker",
            )
            self._owns_crypto_executor = True

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

        self._queue: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._session = None  # aiohttp.ClientSession
        self._ws = None       # aiohttp.ClientWebSocketResponse
        self._recv_task: Optional[asyncio.Task] = None
        self._buffer = bytearray()

    async def connect(self, address: Tuple[str, int]) -> None:
        host, port = address
        url = f"wss://{host}:{port}/apiws"

        log.info("WS connecting to %s", url)

        self._session = aiohttp.ClientSession()

        try:
            self._ws = await asyncio.wait_for(
                self._session.ws_connect(url, protocols=["binary"]),
                timeout=CONNECT_TIMEOUT,
            )
        except Exception:
            await self._session.close()
            self._session = None
            raise

        # Send nonce as first binary message
        nonce = self._obfuscation.generate_nonce()
        await self._ws.send_bytes(nonce)

        # Start receive loop
        self._recv_task = asyncio.get_event_loop().create_task(self._ws_recv_loop())

        log.info("WS connection established to %s", url)

    async def _ws_recv_loop(self) -> None:
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    data = self._obfuscation.decrypt(msg.data)
                    self._buffer.extend(data)

                    while True:
                        result = self._codec.decode(self._buffer)
                        if result is None:
                            break

                        payload, ack_token = result

                        if ack_token is not None:
                            if self.quick_ack_handler is not None:
                                self.quick_ack_handler(ack_token)
                            continue

                        if payload is None:
                            continue

                        try:
                            self._queue.put_nowait(payload)
                        except asyncio.QueueFull:
                            log.warning("WS frame queue full, dropping frame")

                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.warning("WS error: %s", self._ws.exception())
                    break
        except asyncio.CancelledError:
            return
        except Exception:
            log.exception("WS recv loop error")
        finally:
            # EOF sentinel
            try:
                self._queue.put_nowait(None)
            except asyncio.QueueFull:
                pass

    async def send(self, data: bytes, request_ack: bool = False) -> None:
        if self._ws is None or self._ws.closed:
            raise OSError("WebSocket connection is closed")

        encoded = self._codec.encode(data, request_ack=request_ack)
        encrypted = await self.loop.run_in_executor(
            self.crypto_executor, self._obfuscation.encrypt, encoded,
        )
        await self._ws.send_bytes(encrypted)

    async def recv(self) -> Optional[bytes]:
        return await self._queue.get()

    async def close(self) -> None:
        if self._recv_task is not None and not self._recv_task.done():
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
            self._recv_task = None

        if self._ws is not None and not self._ws.closed:
            await self._ws.close()
            self._ws = None

        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

        if self._owns_crypto_executor:
            self.crypto_executor.shutdown(wait=False)


# --- Factory functions ---

def WSAbridgedO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> WSTransport:
    return WSTransport(
        codec=AbridgedCodec(),
        obfuscation=ObfuscationLayer(b"\xef\xef\xef\xef"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def WSIntermediateO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> WSTransport:
    return WSTransport(
        codec=IntermediateCodec(),
        obfuscation=ObfuscationLayer(b"\xee\xee\xee\xee"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def WSPaddedIntermediateO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> WSTransport:
    return WSTransport(
        codec=PaddedIntermediateCodec(),
        obfuscation=ObfuscationLayer(b"\xdd\xdd\xdd\xdd"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )
