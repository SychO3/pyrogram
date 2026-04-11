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
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, Union
from urllib.parse import parse_qs

log = logging.getLogger(__name__)


class WS:
    CONNECT_TIMEOUT = 10
    SEND_TIMEOUT = 10

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Union[str, dict, None] = None,
        crypto_executor_workers: int = 1,
    ) -> None:
        self.ipv6 = ipv6
        self.proxy = proxy

        self.crypto_executor_workers = crypto_executor_workers
        self.crypto_executor = ThreadPoolExecutor(
            max_workers=self.crypto_executor_workers, thread_name_prefix="CryptoWorker"
        )

        self._session = None  # aiohttp.ClientSession
        self._ws = None  # aiohttp.ClientWebSocketResponse
        self._recv_task: Optional[asyncio.Task] = None
        self._recv_queue: asyncio.Queue = asyncio.Queue(maxsize=256)

        self.marker_event = asyncio.Event()
        self.lock = asyncio.Lock()
        self.quick_ack_handler = None

    def _build_proxy_url(self) -> Optional[str]:
        if self.proxy is None:
            return None

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
                    raise ValueError(
                        "Telegram proxy link must contain 'server' and 'port' params"
                    )
                if user and password:
                    return f"http://{user}:{password}@{server}:{port}"
                return f"http://{server}:{port}"

            return self.proxy

        scheme = self.proxy.get("scheme", "http").lower()
        hostname = self.proxy.get("hostname")
        port = self.proxy.get("port")
        username = self.proxy.get("username")
        password = self.proxy.get("password")

        if not hostname or not port:
            raise ValueError("Proxy dict must contain 'hostname' and 'port'")

        if username and password:
            return f"{scheme}://{username}:{password}@{hostname}:{port}"
        return f"{scheme}://{hostname}:{port}"

    async def connect(self, address: Tuple[str, int]) -> None:
        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp is required for WebSocket transport. "
                "Install it with: pip install aiohttp"
            )

        host, port = address
        url = f"wss://{host}:{port}/apiws"
        proxy_url = self._build_proxy_url()

        log.info("Connecting to %s (WebSocket)", url)

        self._session = aiohttp.ClientSession()
        try:
            self._ws = await asyncio.wait_for(
                self._session.ws_connect(url, proxy=proxy_url, protocols=["binary"]),
                timeout=self.CONNECT_TIMEOUT,
            )
        except asyncio.TimeoutError:
            await self._session.close()
            self._session = None
            raise TimeoutError("WebSocket connection timed out")
        except Exception:
            await self._session.close()
            self._session = None
            raise

        log.info("WebSocket connection established")

        self._recv_task = asyncio.get_event_loop().create_task(self._recv_loop())

    async def _recv_loop(self) -> None:
        import aiohttp

        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    await self._recv_queue.put(msg.data)
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.warning("WebSocket error: %s", self._ws.exception())
                    break
        except asyncio.CancelledError:
            return
        except Exception as e:
            log.warning("WebSocket recv loop error: %s %s", type(e).__name__, e)
        finally:
            await self._recv_queue.put(None)

    async def send(self, data: bytes, wait_for_marker: bool = True) -> None:
        if wait_for_marker:
            try:
                await asyncio.wait_for(self.marker_event.wait(), timeout=self.SEND_TIMEOUT)
            except asyncio.TimeoutError:
                raise TimeoutError("Timed out waiting for transport handshake")

        async with self.lock:
            if self._ws is None or self._ws.closed:
                raise OSError("WebSocket connection is closed")

            log.debug("Sending %d bytes (WebSocket)", len(data))
            await self._ws.send_bytes(data)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        try:
            data = await self._recv_queue.get()
        except Exception:
            return None

        if data is None:
            return None

        return data

    async def close(self) -> None:
        if self._recv_task is not None:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except (asyncio.CancelledError, Exception):
                pass
            self._recv_task = None

        if self._ws is not None and not self._ws.closed:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        if self._session is not None:
            try:
                await self._session.close()
            except Exception:
                pass
            self._session = None

        self.crypto_executor.shutdown(wait=False)
