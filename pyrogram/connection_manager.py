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
import random
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from pyrogram.bot_handle import BotHandle
    from pyrogram.connection import Connection
    from pyrogram.runtime import Runtime
    from pyrogram.session import Session

log = logging.getLogger(__name__)

# DC failure coordination
DC_FAILURE_WINDOW = 10.0  # seconds
DC_FAILURE_THRESHOLD = 5  # failures within window to trigger cooldown
DC_COOLDOWN_BASE = 5.0
DC_COOLDOWN_MAX = 60.0


@dataclass
class ManagedConnection:
    session: "Session"
    bot_id: int
    dc_id: int
    last_active: float = field(default_factory=time.monotonic)
    idle: bool = False


class ConnectionManager:
    """Manages TCP connections across all bots.

    Supports multiple connections per bot per DC.
    Handles idle reaping and DC-level reconnect coordination.
    """

    def __init__(
        self,
        runtime: "Runtime",
        idle_timeout: float = 60.0,
        max_connections_per_dc: int = 100,
    ):
        self._runtime = runtime
        self.idle_timeout = idle_timeout
        self.max_connections_per_dc = max_connections_per_dc

        # dc_id -> {bot_id -> list[ManagedConnection]}
        self._connections: Dict[int, Dict[int, List[ManagedConnection]]] = {}
        self._lock = asyncio.Lock()

        # DC failure tracking
        self._dc_failures: Dict[int, List[float]] = {}  # dc_id -> [timestamps]
        self._dc_cooldown_until: Dict[int, float] = {}  # dc_id -> monotonic deadline
        self._dc_consecutive_failures: Dict[int, int] = {}

        # Idle reaper
        self._reaper_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._reaper_task = asyncio.get_event_loop().create_task(self._idle_reaper())

    async def stop(self) -> None:
        if self._reaper_task and not self._reaper_task.done():
            self._reaper_task.cancel()
            try:
                await self._reaper_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        async with self._lock:
            for dc_id, bot_conns in self._connections.items():
                for bot_id, conns in bot_conns.items():
                    for mc in conns:
                        try:
                            await mc.session.stop()
                        except Exception as e:
                            log.debug("Error closing connection for bot %d DC%d: %s", bot_id, dc_id, e)
            self._connections.clear()

    def get_active_connections(self, bot_id: int, dc_id: int) -> List[ManagedConnection]:
        return self._connections.get(dc_id, {}).get(bot_id, [])

    async def register_session(self, bot_id: int, dc_id: int, session: "Session") -> ManagedConnection:
        async with self._lock:
            dc_conns = self._connections.setdefault(dc_id, {})
            bot_conns = dc_conns.setdefault(bot_id, [])

            mc = ManagedConnection(
                session=session,
                bot_id=bot_id,
                dc_id=dc_id,
            )
            bot_conns.append(mc)
            return mc

    async def mark_active(self, mc: ManagedConnection) -> None:
        mc.last_active = time.monotonic()
        mc.idle = False

    async def mark_idle(self, mc: ManagedConnection) -> None:
        mc.idle = True
        mc.last_active = time.monotonic()

    def _find_connection(self, bot_id: int, dc_id: int) -> Optional[ManagedConnection]:
        """Find the first registered connection for a bot on a DC."""
        conns = self._connections.get(dc_id, {}).get(bot_id, [])
        return conns[0] if conns else None

    @asynccontextmanager
    async def acquire(self, bot_id: int, dc_id: int):
        """Acquire a connection, marking it active for the duration.

        Usage::

            async with connection_mgr.acquire(bot_id, dc_id) as mc:
                await mc.session.send(data)
        """
        mc = self._find_connection(bot_id, dc_id)
        if mc is None:
            raise ConnectionError(f"No connection for bot {bot_id} DC{dc_id}")
        await self.mark_active(mc)
        try:
            yield mc
        finally:
            await self.mark_idle(mc)

    async def remove_connection(self, mc: ManagedConnection) -> None:
        async with self._lock:
            bot_conns = self._connections.get(mc.dc_id, {}).get(mc.bot_id, [])
            try:
                bot_conns.remove(mc)
            except ValueError:
                pass

    async def remove_bot(self, bot_id: int) -> List[ManagedConnection]:
        removed = []
        async with self._lock:
            for dc_id, bot_conns in list(self._connections.items()):
                if bot_id in bot_conns:
                    removed.extend(bot_conns.pop(bot_id))
                    if not bot_conns:
                        del self._connections[dc_id]
        return removed

    async def _idle_reaper(self) -> None:
        log.info("Idle reaper started (timeout=%.0fs)", self.idle_timeout)
        while True:
            try:
                await asyncio.sleep(self.idle_timeout / 2)
            except asyncio.CancelledError:
                return

            now = time.monotonic()
            to_close = []

            async with self._lock:
                for dc_id, bot_conns in self._connections.items():
                    for bot_id, conns in bot_conns.items():
                        expired = [
                            mc for mc in conns
                            if mc.idle and (now - mc.last_active) > self.idle_timeout
                        ]
                        for mc in expired:
                            conns.remove(mc)
                            to_close.append(mc)

            for mc in to_close:
                log.info(
                    "Closing idle connection: bot=%d DC%d (idle %.0fs)",
                    mc.bot_id, mc.dc_id, now - mc.last_active,
                )
                try:
                    await mc.session.stop()
                except Exception as e:
                    log.debug("Error closing idle session: %s", e)

    # --- DC failure coordination ---

    async def on_connection_lost(self, dc_id: int, bot_id: int) -> float:
        """Record a connection loss and return recommended backoff delay.

        If multiple connections to the same DC fail within a short window,
        applies DC-level coordinated backoff to prevent thundering herd.
        Also removes the connection from tracking and records metrics.
        """
        now = time.monotonic()

        # Remove from active connections
        async with self._lock:
            bot_conns = self._connections.get(dc_id, {}).get(bot_id, [])
            # Remove the first matching connection (most likely the lost one)
            removed = None
            for mc in bot_conns:
                if mc.dc_id == dc_id and mc.bot_id == bot_id:
                    removed = mc
                    break
            if removed is not None:
                bot_conns.remove(removed)

        # Record metrics
        if hasattr(self._runtime, 'metrics'):
            self._runtime.metrics.record_connection_close(dc_id)
            self._runtime.metrics.record_transport_error()

        # Record failure
        failures = self._dc_failures.setdefault(dc_id, [])
        failures.append(now)
        # Trim old failures
        failures[:] = [t for t in failures if now - t < DC_FAILURE_WINDOW]

        if len(failures) >= DC_FAILURE_THRESHOLD:
            # DC-level failure detected
            consecutive = self._dc_consecutive_failures.get(dc_id, 0) + 1
            self._dc_consecutive_failures[dc_id] = consecutive

            cooldown = min(
                DC_COOLDOWN_BASE * (2 ** min(consecutive - 1, 5)),
                DC_COOLDOWN_MAX,
            )
            # Add jitter
            cooldown *= 0.5 + random.random()
            self._dc_cooldown_until[dc_id] = now + cooldown

            log.warning(
                "DC%d failure burst detected (%d failures in %.0fs). "
                "Cooldown: %.1fs (consecutive: %d)",
                dc_id, len(failures), DC_FAILURE_WINDOW, cooldown, consecutive,
            )
            return cooldown

        # Reset consecutive counter if not in burst
        self._dc_consecutive_failures[dc_id] = 0
        return 0.0

    async def get_dc_cooldown(self, dc_id: int) -> float:
        """Return remaining cooldown seconds for a DC, or 0 if none."""
        deadline = self._dc_cooldown_until.get(dc_id, 0)
        remaining = deadline - time.monotonic()
        return max(0.0, remaining)

    def connection_count(self, dc_id: Optional[int] = None) -> int:
        if dc_id is not None:
            return sum(
                len(conns)
                for conns in self._connections.get(dc_id, {}).values()
            )
        return sum(
            len(conns)
            for bot_conns in self._connections.values()
            for conns in bot_conns.values()
        )
