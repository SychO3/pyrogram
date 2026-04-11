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

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, Callable, Dict, Optional, Type, Union

from pyrogram import utils
from pyrogram.bot_handle import BotConfig, BotHandle
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCP, TCPAbridged, ProtoAbridged
from pyrogram.connection_manager import ConnectionManager
from pyrogram.crypto import mtproto
from pyrogram.storage import MultiSQLiteStorage, SessionData
from pyrogram.update_dispatcher import UpdateDispatcher

log = logging.getLogger(__name__)

# Graceful shutdown constants
SHUTDOWN_RPC_TIMEOUT = 5.0  # seconds to wait for in-flight RPCs
AUTH_CONCURRENCY_LIMIT = 50  # max concurrent DH exchanges


@dataclass
class RuntimeMetrics:
    """Runtime observability metrics."""

    # Connection pool
    active_connections: int = 0
    active_connections_per_dc: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    connection_creates_total: int = 0
    connection_closes_total: int = 0

    # Bot state
    total_bots: int = 0
    active_bots: int = 0
    bots_by_state: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Throughput
    rpc_requests_total: int = 0
    rpc_errors_total: int = 0
    updates_received_total: int = 0

    # Errors
    flood_waits_total: int = 0
    transport_errors_total: int = 0
    reconnects_total: int = 0

    # Internal
    _on_metrics: Optional[Callable] = field(default=None, repr=False)

    def snapshot(self) -> dict:
        return {
            "active_connections": self.active_connections,
            "active_connections_per_dc": dict(self.active_connections_per_dc),
            "connection_creates_total": self.connection_creates_total,
            "connection_closes_total": self.connection_closes_total,
            "total_bots": self.total_bots,
            "active_bots": self.active_bots,
            "bots_by_state": dict(self.bots_by_state),
            "rpc_requests_total": self.rpc_requests_total,
            "rpc_errors_total": self.rpc_errors_total,
            "updates_received_total": self.updates_received_total,
            "flood_waits_total": self.flood_waits_total,
            "transport_errors_total": self.transport_errors_total,
            "reconnects_total": self.reconnects_total,
        }

    def record_connection_create(self, dc_id: int) -> None:
        self.active_connections += 1
        self.active_connections_per_dc[dc_id] += 1
        self.connection_creates_total += 1
        self._notify()

    def record_connection_close(self, dc_id: int) -> None:
        self.active_connections = max(0, self.active_connections - 1)
        if dc_id in self.active_connections_per_dc:
            self.active_connections_per_dc[dc_id] = max(
                0, self.active_connections_per_dc[dc_id] - 1
            )
        self.connection_closes_total += 1
        self._notify()

    def record_rpc_request(self) -> None:
        self.rpc_requests_total += 1

    def record_rpc_error(self) -> None:
        self.rpc_errors_total += 1

    def record_update(self) -> None:
        self.updates_received_total += 1

    def record_flood_wait(self) -> None:
        self.flood_waits_total += 1

    def record_transport_error(self) -> None:
        self.transport_errors_total += 1

    def record_reconnect(self) -> None:
        self.reconnects_total += 1

    def _notify(self) -> None:
        if self._on_metrics is not None:
            try:
                self._on_metrics(self.snapshot())
            except Exception:
                pass


class Runtime:
    """Multi-tenant MTProto runtime.

    Manages shared resources (thread pools, storage, connections) for
    multiple bots in a single process. Each bot gets a BotHandle with
    per-bot state that delegates to shared infrastructure.

    Usage::

        runtime = Runtime(storage_path="bots.db")
        await runtime.start()
        bot = await runtime.add_bot(
            SessionData(bot_id=123, auth_key=b"..."),
            BotConfig(api_id=12345),
        )
        # ... use bot ...
        await runtime.remove_bot(123)
        await runtime.stop()
    """

    def __init__(
        self,
        crypto_workers: Optional[int] = None,
        storage_path: str = "bots.db",
        storage_backend: str = "sqlite",
        redis_uri: str = "redis://localhost:6379/0",
        max_connections_per_dc: int = 100,
        idle_timeout: float = 60.0,
        handler_workers: int = 32,
        dispatcher_workers: int = 32,
        proxy: Optional[Union[dict, str]] = None,
        connection_factory: Type = Connection,
        protocol_factory = ProtoAbridged,
        on_metrics: Optional[Callable] = None,
    ):
        self._crypto_workers = crypto_workers or (os.cpu_count() or 2)
        self._storage_path = storage_path
        self._storage_backend = storage_backend
        self._redis_uri = redis_uri
        self._handler_workers = handler_workers
        self._dispatcher_workers = dispatcher_workers
        self._idle_timeout = idle_timeout
        self._max_connections_per_dc = max_connections_per_dc

        self.proxy = proxy
        self.connection_factory = connection_factory
        self.protocol_factory = protocol_factory

        self.crypto_executor: Optional[ThreadPoolExecutor] = None
        self.handler_executor: Optional[ThreadPoolExecutor] = None

        self.storage: Optional[Any] = None  # MultiSQLiteStorage or RedisStorage
        self.connection_mgr: Optional[ConnectionManager] = None
        self.update_dispatcher: Optional[UpdateDispatcher] = None

        self.metrics = RuntimeMetrics(_on_metrics=on_metrics)

        self.bots: Dict[int, BotHandle] = {}
        self._auth_key_index: Dict[bytes, BotHandle] = {}

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._started = False
        self._stopping = False

        # Auth key exchange concurrency control
        self._auth_semaphore = asyncio.Semaphore(AUTH_CONCURRENCY_LIMIT)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = utils.get_event_loop()
        return self._loop

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("Runtime already started")

        self._loop = asyncio.get_event_loop()

        # Shared executors
        self.crypto_executor = ThreadPoolExecutor(
            max_workers=self._crypto_workers,
            thread_name_prefix="RuntimeCrypto",
        )
        self.handler_executor = ThreadPoolExecutor(
            max_workers=self._handler_workers,
            thread_name_prefix="RuntimeHandler",
        )

        # Storage
        if self._storage_backend == "redis":
            from pyrogram.storage.redis_storage import RedisStorage
            self.storage = RedisStorage(self._redis_uri)
        else:
            self.storage = MultiSQLiteStorage(self._storage_path)
        await self.storage.open()

        # Connection manager
        self.connection_mgr = ConnectionManager(
            self,
            idle_timeout=self._idle_timeout,
            max_connections_per_dc=self._max_connections_per_dc,
        )
        await self.connection_mgr.start()

        # Update dispatcher
        self.update_dispatcher = UpdateDispatcher(self, worker_count=self._dispatcher_workers)
        await self.update_dispatcher.start()

        self._started = True
        log.info(
            "Runtime started (crypto=%d, handlers=%d, dispatchers=%d, storage=%s)",
            self._crypto_workers, self._handler_workers,
            self._dispatcher_workers, self._storage_backend,
        )

        # Load existing sessions (batch startup)
        sessions = await self.storage.read_all_sessions()
        for session_data in sessions:
            if session_data.auth_key:
                try:
                    bot = self._register_bot_handle(session_data)
                    await self._init_bot(bot)
                except Exception:
                    log.exception("Failed to load bot %d", session_data.bot_id)

        if sessions:
            log.info("Loaded %d bot(s) from storage", len(self.bots))

    async def stop(self) -> None:
        """Graceful shutdown sequence.

        1. Stop accepting new bots
        2. Send pending ACKs and wait for in-flight RPCs (with timeout)
        3. Stop all bot sessions
        4. Close all connections via ConnectionManager
        5. Stop update dispatcher
        6. Drain and close storage
        7. Shutdown executors
        """
        if not self._started or self._stopping:
            return

        self._stopping = True
        log.info("Runtime stopping (%d bots)...", len(self.bots))

        # Phase 1: Send pending ACKs for all sessions
        ack_tasks = []
        for bot in list(self.bots.values()):
            if bot.session is not None and hasattr(bot.session, 'pending_acks') and bot.session.pending_acks:
                async def _flush_acks(session):
                    try:
                        from pyrogram import raw
                        await session.send(
                            raw.types.MsgsAck(msg_ids=list(session.pending_acks)),
                            wait_response=False
                        )
                        session.pending_acks.clear()
                    except Exception:
                        pass
                ack_tasks.append(_flush_acks(bot.session))

        if ack_tasks:
            await asyncio.gather(*ack_tasks, return_exceptions=True)

        # Phase 2: Wait for in-flight RPCs with timeout
        rpc_wait_tasks = []
        for bot in list(self.bots.values()):
            if bot.session is not None and hasattr(bot.session, 'results'):
                for result in list(bot.session.results.values()):
                    if result.value is None:
                        rpc_wait_tasks.append(result.event.wait())

        if rpc_wait_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*rpc_wait_tasks, return_exceptions=True),
                    timeout=SHUTDOWN_RPC_TIMEOUT,
                )
            except asyncio.TimeoutError:
                log.warning("Timed out waiting for %d in-flight RPCs", len(rpc_wait_tasks))

        # Phase 3: Stop all bot sessions (main + media + aux)
        stop_tasks = []
        for bot in list(self.bots.values()):
            if bot.session is not None:
                stop_tasks.append(bot.session.stop())
            for session in list(bot.sessions.values()):
                stop_tasks.append(session.stop())
            for session in list(bot.media_sessions.values()):
                stop_tasks.append(session.stop())
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        # Phase 4: Close all connections
        if self.connection_mgr:
            await self.connection_mgr.stop()

        # Phase 5: Stop update dispatcher
        if self.update_dispatcher:
            await self.update_dispatcher.stop()

        # Phase 5.5: Save update state for all bots
        for bot in self.bots.values():
            try:
                await bot.save_update_state()
            except Exception:
                log.debug("Failed to save update state for bot %d", bot.bot_id)

        # Phase 6: Close storage (drains write queue internally)
        if self.storage:
            await self.storage.close()

        # Phase 7: Shutdown executors
        if self.crypto_executor:
            self.crypto_executor.shutdown(wait=False)
        if self.handler_executor:
            self.handler_executor.shutdown(wait=False)

        self.bots.clear()
        self._auth_key_index.clear()

        self._started = False
        self._stopping = False
        log.info("Runtime stopped")

    def _register_bot_handle(self, data: SessionData, config: Optional[BotConfig] = None) -> BotHandle:
        if config is None:
            config = BotConfig(api_id=data.api_id or 0)

        bot = BotHandle(
            runtime=self,
            bot_id=data.bot_id,
            config=config,
            auth_key=data.auth_key or b"",
        )

        self.bots[data.bot_id] = bot
        if bot.auth_key_id:
            self._auth_key_index[bot.auth_key_id] = bot

        self.update_dispatcher.register_bot(data.bot_id)
        self.metrics.total_bots = len(self.bots)

        return bot

    async def _init_bot(self, bot: BotHandle) -> None:
        """Post-registration async initialization (load update state, etc.)."""
        await bot.load_update_state()

    async def add_bot(
        self,
        session_data: SessionData,
        config: Optional[BotConfig] = None,
    ) -> BotHandle:
        if not self._started:
            raise RuntimeError("Runtime not started")
        if self._stopping:
            raise RuntimeError("Runtime is stopping")
        if session_data.bot_id in self.bots:
            raise ValueError(f"Bot {session_data.bot_id} already registered")

        # Save session data
        await self.storage.save_session(session_data)

        bot = self._register_bot_handle(session_data, config)
        await self._init_bot(bot)
        log.info("Bot %d added", session_data.bot_id)

        return bot

    async def add_bot_from_file(
        self,
        session_file: str,
        bot_id: int,
        config: Optional[BotConfig] = None,
    ) -> BotHandle:
        if not self._started:
            raise RuntimeError("Runtime not started")

        data = await self.storage.migrate_from_file(session_file, bot_id)
        if data is None:
            raise FileNotFoundError(f"Session file not found: {session_file}")

        bot = self._register_bot_handle(data, config)
        await self._init_bot(bot)
        log.info("Bot %d migrated from %s", bot_id, session_file)

        return bot

    async def remove_bot(self, bot_id: int) -> None:
        bot = self.bots.get(bot_id)
        if bot is None:
            raise KeyError(f"Bot {bot_id} not found")

        # Stop session
        if bot.session is not None:
            try:
                await bot.session.stop()
            except Exception:
                log.exception("Error stopping session for bot %d", bot_id)

        # Fail pending results on all sessions
        for session in list(bot.sessions.values()) + list(bot.media_sessions.values()):
            try:
                await session.stop()
            except Exception:
                pass

        # Release connections
        removed = await self.connection_mgr.remove_bot(bot_id)
        for mc in removed:
            try:
                await mc.session.stop()
            except Exception:
                pass

        # Cleanup dispatcher
        self.update_dispatcher.unregister_bot(bot_id)

        # Remove from indices
        if bot.auth_key_id in self._auth_key_index:
            del self._auth_key_index[bot.auth_key_id]
        del self.bots[bot_id]

        self.metrics.total_bots = len(self.bots)
        log.info("Bot %d removed", bot_id)

    def get_bot_by_auth_key_id(self, auth_key_id: bytes) -> Optional[BotHandle]:
        return self._auth_key_index.get(auth_key_id)

    # --- Crypto operations ---

    async def encrypt(self, auth_key: bytes, auth_key_id: bytes,
                      message: Any, salt: int, session_id: bytes) -> bytes:
        self.metrics.record_rpc_request()
        return await self.loop.run_in_executor(
            self.crypto_executor,
            mtproto.pack,
            message, salt, session_id, auth_key, auth_key_id,
        )

    async def decrypt(self, auth_key: bytes, auth_key_id: bytes,
                      packet: bytes, session_id: bytes) -> Any:
        return await self.loop.run_in_executor(
            self.crypto_executor,
            mtproto.unpack,
            BytesIO(packet), session_id, auth_key, auth_key_id,
        )

    # --- Auth key exchange ---

    async def create_auth_key(
        self,
        bot: BotHandle,
        dc_id: int,
        server_address: str,
        port: int,
        test_mode: bool,
    ) -> bytes:
        """Create an auth key for a bot, with concurrency control.

        Uses a semaphore to limit concurrent DH exchanges across all bots.
        """
        async with self._auth_semaphore:
            from pyrogram.session.auth import Auth

            auth = Auth(
                client=bot,
                dc_id=dc_id,
                server_address=server_address,
                port=port,
                test_mode=test_mode,
            )
            auth_key = await auth.create()

            # Update bot's auth key
            from hashlib import sha1
            bot.auth_key = auth_key
            bot.auth_key_id = sha1(auth_key).digest()[-8:]
            self._auth_key_index[bot.auth_key_id] = bot

            # Persist
            await bot.storage.auth_key(auth_key)

            log.info("Auth key created for bot %d on DC%d", bot.bot_id, dc_id)
            return auth_key

    # --- Reconnection ---

    async def on_bot_connection_lost(self, bot_id: int, dc_id: int) -> None:
        """Called by ConnectionManager when a bot's connection is lost."""
        bot = self.bots.get(bot_id)
        if bot is None:
            return

        self.metrics.record_reconnect()

        # Get coordinated backoff from ConnectionManager
        backoff = await self.connection_mgr.on_connection_lost(dc_id, bot_id)

        if backoff > 0:
            log.info("Bot %d DC%d: coordinated backoff %.1fs", bot_id, dc_id, backoff)

        # Session.restart() handles its own reconnection logic
        # We just record the event here

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()

    def __repr__(self) -> str:
        return (
            f"Runtime(bots={len(self.bots)}, "
            f"connections={self.connection_mgr.connection_count() if self.connection_mgr else 0})"
        )
