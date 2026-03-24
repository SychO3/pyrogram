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
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, TypedDict, Union

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy

from pyrogram import utils

log = logging.getLogger(__name__)


class ProxyDict(TypedDict):
    scheme: str
    hostname: str
    port: int
    username: Optional[str]
    password: Optional[str]


class TCP:
    TIMEOUT = 6

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Union[str, ProxyDict, None] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self.ipv6 = ipv6
        self.proxy = proxy

        self.crypto_executor_workers = crypto_executor_workers
        self.crypto_executor = ThreadPoolExecutor(
            max_workers=self.crypto_executor_workers, thread_name_prefix="CryptoWorker"
        )

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.marker_event = asyncio.Event()
        self.lock = asyncio.Lock()
        self.quick_ack_handler = None

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

    async def _build_proxy(self) -> Proxy:
        if isinstance(self.proxy, str):
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

    async def _connect_via_proxy(self, destination: Tuple[str, int]) -> None:
        dest_host, dest_port = destination
        proxy = await self._build_proxy()

        log.info(
            "Connecting to %s:%s via proxy %s",
            dest_host,
            dest_port,
            self.proxy,
        )

        try:
            sock = await proxy.connect(
                dest_host=dest_host,
                dest_port=dest_port,
                timeout=TCP.TIMEOUT,
            )
        except Exception as e:
            log.error("Proxy connection failed: %s %s", type(e).__name__, e)
            raise

        log.info("Proxy connection established")

        self.reader, self.writer = await asyncio.open_connection(sock=sock)

    async def _connect_via_direct(self, destination: Tuple[str, int]) -> None:
        host, port = destination
        family = socket.AF_INET6 if self.ipv6 else socket.AF_INET

        log.info("Connecting to %s:%s", host, port)

        try:
            self.reader, self.writer = await asyncio.open_connection(
                host=host,
                port=port,
                family=family,
            )
        except Exception as e:
            log.error("Connection failed: %s %s", type(e).__name__, e)
            raise

        log.info("Connection established")

    def _set_socket_options(self) -> None:
        if self.writer is None:
            return
        sock = self.writer.transport.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    async def _connect(self, destination: Tuple[str, int]) -> None:
        if self.proxy:
            await self._connect_via_proxy(destination)
        else:
            await self._connect_via_direct(destination)
        self._set_socket_options()

    async def connect(self, address: Tuple[str, int]) -> None:
        try:
            await asyncio.wait_for(self._connect(address), timeout=TCP.TIMEOUT)
        except asyncio.TimeoutError:  # Re-raise as TimeoutError. asyncio.TimeoutError is deprecated in 3.11
            raise TimeoutError("Connection timed out")

    async def close(self) -> None:
        async with self.lock:
            if self.writer is None or self.writer.is_closing():
                log.debug("Close called but writer is already None or closing, skipping")
                return None

            try:
                if self.writer.transport is not None:
                    self.writer.transport.abort()

                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), timeout=TCP.TIMEOUT)
            except asyncio.TimeoutError:
                log.warning("Disconnect timed out after %ss", TCP.TIMEOUT)
            except Exception as e:
                log.info("Close exception: %s %s", type(e).__name__, e)
            finally:
                self.writer = None

        self.crypto_executor.shutdown(wait=False)

    async def send(self, data: bytes, wait_for_marker: bool = True) -> None:
        if wait_for_marker:
            try:
                await asyncio.wait_for(self.marker_event.wait(), timeout=TCP.TIMEOUT)
            except asyncio.TimeoutError:
                raise TimeoutError("Timed out waiting for transport handshake")

        async with self.lock:
            if self.writer is None or self.writer.is_closing():
                raise OSError("Connection is closed")

            log.debug("Sending %d bytes", len(data))
            try:
                self.writer.write(data)
                await asyncio.wait_for(self.writer.drain(), timeout=TCP.TIMEOUT)
            except asyncio.TimeoutError:
                raise OSError("Send drain timed out")
            except OSError:
                raise
            except Exception as e:
                raise OSError(str(e)) from e

    async def recv(self, length: int = 0) -> Optional[bytes]:
        if not self.reader:
            log.debug("Recv called but reader is None")
            return None

        log.debug("Receiving %d bytes", length)
        buf = bytearray()

        while len(buf) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(buf)),
                    timeout=TCP.TIMEOUT,
                )
            except asyncio.TimeoutError:
                log.debug(
                    "Recv timed out after %ss (got %d/%d bytes)", TCP.TIMEOUT, len(buf), length
                )
                return None
            except OSError as e:
                log.debug("Recv OSError: %s %s", type(e).__name__, e)
                return None
            else:
                if chunk:
                    buf.extend(chunk)
                    log.debug(
                        "Received chunk: %d bytes (%d/%d total)", len(chunk), len(buf), length
                    )
                else:
                    log.debug(
                        "Recv got empty chunk (connection closed?) after %d/%d bytes",
                        len(buf),
                        length,
                    )
                    return None

        log.debug("Recv complete: %d bytes", len(buf))
        return bytes(buf)
