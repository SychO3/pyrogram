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

"""TransportBase adapter for asyncio.Protocol-based transports."""

import asyncio
import logging
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, Type, Union
from urllib.parse import parse_qs

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy

from pyrogram import utils
from pyrogram.connection.transport.base import TransportBase
from pyrogram.connection.transport.codec import (
    AbridgedCodec,
    FrameCodec,
    FullCodec,
    IntermediateCodec,
    PaddedIntermediateCodec,
)
from pyrogram.connection.transport.obfuscation import ObfuscationLayer
from pyrogram.connection.transport.proto.mtproto_protocol import MTProtoProtocol

log = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10


class ProtoTransport(TransportBase):
    """asyncio.Protocol-based MTProto transport.

    Wraps MTProtoProtocol with the TransportBase interface. Frames are
    pushed into an asyncio.Queue by the protocol, and recv() pulls
    from that queue — bridging push-model I/O to the pull-model
    expected by Session.recv_worker.
    """

    def __init__(
        self,
        codec: FrameCodec,
        obfuscation: Optional[ObfuscationLayer] = None,
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
        self._protocol: Optional[MTProtoProtocol] = None
        self._transport: Optional[asyncio.Transport] = None

    @property
    def protocol(self) -> Optional[MTProtoProtocol]:
        return self._protocol

    async def _build_proxy(self) -> Proxy:
        if isinstance(self.proxy, str):
            match = re.match(
                r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/socks\?|tg://socks\?)(.+)",
                self.proxy,
            )

            if match:
                params = parse_qs(match.group(1))
                server = params.get("server", [None])[0]
                port = params.get("port", [None])[0]
                user = params.get("user", [None])[0]
                password = params.get("pass", [None])[0]

                if not server or not port:
                    raise ValueError("Telegram proxy link must contain 'server' and 'port' params")

                if user and password:
                    url = f"socks5://{user}:{password}@{server}:{port}"
                else:
                    url = f"socks5://{server}:{port}"

                return Proxy.from_url(url)

            return Proxy.from_url(self.proxy)

        scheme = self.proxy.get("scheme", "").lower()
        hostname = self.proxy.get("hostname")
        port = self.proxy.get("port")
        username = self.proxy.get("username")
        password = self.proxy.get("password")

        if not scheme or not hostname or not port:
            raise ValueError("Proxy dict must contain 'scheme', 'hostname', and 'port'")

        if username and password:
            url = f"{scheme}://{username}:{password}@{hostname}:{port}"
        else:
            url = f"{scheme}://{hostname}:{port}"

        return Proxy.from_url(url)

    async def connect(self, address: Tuple[str, int]) -> None:
        host, port = address
        loop = asyncio.get_event_loop()

        def protocol_factory():
            return MTProtoProtocol(
                codec=self._codec,
                obfuscation=self._obfuscation,
                frame_queue=self._queue,
                ack_source=self,
            )

        if self.proxy:
            proxy = await self._build_proxy()
            log.info("Connecting to %s:%s via proxy %s", host, port, self.proxy)
            sock = await proxy.connect(dest_host=host, dest_port=port, timeout=CONNECT_TIMEOUT)
            transport, protocol = await asyncio.wait_for(
                loop.create_connection(protocol_factory, sock=sock),
                timeout=CONNECT_TIMEOUT,
            )
        else:
            family = socket.AF_INET6 if self.ipv6 else socket.AF_INET
            log.info("Connecting to %s:%s", host, port)
            transport, protocol = await asyncio.wait_for(
                loop.create_connection(protocol_factory, host=host, port=port, family=family),
                timeout=CONNECT_TIMEOUT,
            )

        self._transport = transport
        self._protocol = protocol

        # Set TCP options
        sock = transport.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            import sys
            if sys.platform == "linux":
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            elif sys.platform == "darwin":
                TCP_KEEPALIVE = 0x10
                sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 10)

        # Send handshake (nonce or marker)
        if self._obfuscation is not None:
            nonce = self._obfuscation.generate_nonce()
            transport.write(nonce)
        elif self._codec.MARKER is not None:
            transport.write(self._codec.MARKER)

        log.info("Protocol connection established")

    async def send(self, data: bytes, request_ack: bool = False) -> None:
        if self._transport is None or self._transport.is_closing():
            raise OSError("Connection is closed")

        encoded = self._codec.encode(data, request_ack=request_ack)

        if self._obfuscation is not None:
            encoded = await self.loop.run_in_executor(
                self.crypto_executor, self._obfuscation.encrypt, encoded,
            )

        self._transport.write(encoded)

    async def recv(self) -> Optional[bytes]:
        frame = await self._queue.get()

        if self._protocol is not None:
            self._protocol.resume_if_needed()

        return frame  # None = EOF sentinel

    async def close(self) -> None:
        if self._transport is not None and not self._transport.is_closing():
            self._transport.close()

        self._transport = None
        self._protocol = None

        if self._owns_crypto_executor:
            self.crypto_executor.shutdown(wait=False)


# --- Factory functions ---
# Match the existing protocol_factory(ipv6=, proxy=, crypto_executor_workers=, loop=) signature

def ProtoAbridged(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=AbridgedCodec(),
        obfuscation=None,
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def ProtoAbridgedO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=AbridgedCodec(),
        obfuscation=ObfuscationLayer(b"\xef\xef\xef\xef"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def ProtoIntermediate(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=IntermediateCodec(),
        obfuscation=None,
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def ProtoIntermediateO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=IntermediateCodec(),
        obfuscation=ObfuscationLayer(b"\xee\xee\xee\xee"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def ProtoPaddedIntermediateO(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=PaddedIntermediateCodec(),
        obfuscation=ObfuscationLayer(b"\xdd\xdd\xdd\xdd"),
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )


def ProtoFull(
    ipv6: bool = False,
    proxy: Union[dict, str, None] = None,
    crypto_executor_workers: int = 1,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    crypto_executor: Optional[ThreadPoolExecutor] = None,
) -> ProtoTransport:
    return ProtoTransport(
        codec=FullCodec(),
        obfuscation=None,
        ipv6=ipv6, proxy=proxy,
        crypto_executor_workers=crypto_executor_workers,
        loop=loop, crypto_executor=crypto_executor,
    )
