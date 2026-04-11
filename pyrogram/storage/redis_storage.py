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

"""Async Redis storage backend for multi-tenant bot runtime.

Requires ``redis>=5.0`` and ``msgpack``. Install with::

    pip install pyrogram[redis]
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional, Tuple

from pyrogram.storage.session_data import SessionData

log = logging.getLogger(__name__)

# Key prefixes
_SESSION = "kuri:session:"        # hash per bot
_PEERS = "kuri:peers:"            # hash  bot_id -> peer_id -> packed
_USERNAMES = "kuri:usernames:"    # hash  bot_id -> username -> peer_id
_UPDATE_STATE = "kuri:ustate:"    # hash  bot_id -> state_id -> packed
_ALL_BOTS = "kuri:bots"           # set of bot_ids

SESSION_FIELDS = (
    "bot_id", "dc_id", "server_address", "port",
    "api_id", "test_mode", "auth_key", "date", "user_id", "is_bot",
)


class RedisStorage:
    """Async Redis storage backend using redis.asyncio + msgpack.

    Provides the same interface consumed by ``BotStorageProxy`` and ``Runtime``.
    """

    def __init__(self, uri: str = "redis://localhost:6379/0"):
        self._uri = uri
        self._redis = None

    async def open(self) -> None:
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError(
                "redis is required for RedisStorage. "
                "Install it with: pip install pyrogram[redis]"
            )

        self._redis = aioredis.from_url(self._uri, decode_responses=False)
        await self._redis.ping()
        log.info("RedisStorage connected: %s", self._uri)

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
            log.info("RedisStorage closed")

    # --- helpers ---

    @staticmethod
    def _pack(obj: Any) -> bytes:
        import msgpack
        return msgpack.packb(obj, use_bin_type=True)

    @staticmethod
    def _unpack(data: bytes) -> Any:
        import msgpack
        return msgpack.unpackb(data, raw=False)

    def _session_key(self, bot_id: int) -> str:
        return f"{_SESSION}{bot_id}"

    def _peers_key(self, bot_id: int) -> str:
        return f"{_PEERS}{bot_id}"

    def _usernames_key(self, bot_id: int) -> str:
        return f"{_USERNAMES}{bot_id}"

    def _ustate_key(self, bot_id: int) -> str:
        return f"{_UPDATE_STATE}{bot_id}"

    # --- Session CRUD ---

    async def save_session(self, data: SessionData) -> None:
        key = self._session_key(data.bot_id)
        mapping = {
            b"bot_id": self._pack(data.bot_id),
            b"dc_id": self._pack(data.dc_id),
            b"server_address": self._pack(data.server_address),
            b"port": self._pack(data.port),
            b"api_id": self._pack(data.api_id),
            b"test_mode": self._pack(data.test_mode),
            b"auth_key": self._pack(data.auth_key),
            b"date": self._pack(data.date),
            b"user_id": self._pack(data.user_id),
            b"is_bot": self._pack(data.is_bot),
        }
        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.hset(key, mapping=mapping)
            pipe.sadd(_ALL_BOTS, str(data.bot_id).encode())
            await pipe.execute()

    async def read_session(self, bot_id: int) -> Optional[SessionData]:
        key = self._session_key(bot_id)
        raw_data = await self._redis.hgetall(key)
        if not raw_data:
            return None
        return self._session_from_hash(raw_data)

    async def read_all_sessions(self) -> List[SessionData]:
        bot_ids = await self._redis.smembers(_ALL_BOTS)
        if not bot_ids:
            return []

        results = []
        keys = [self._session_key(int(bid)) for bid in bot_ids]

        async with self._redis.pipeline(transaction=False) as pipe:
            for k in keys:
                pipe.hgetall(k)
            raw_list = await pipe.execute()

        for raw_data in raw_list:
            if raw_data:
                results.append(self._session_from_hash(raw_data))

        return results

    async def delete_session(self, bot_id: int) -> None:
        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.delete(self._session_key(bot_id))
            pipe.delete(self._peers_key(bot_id))
            pipe.delete(self._usernames_key(bot_id))
            pipe.delete(self._ustate_key(bot_id))
            pipe.srem(_ALL_BOTS, str(bot_id).encode())
            await pipe.execute()

    def _session_from_hash(self, raw_data: dict) -> SessionData:
        def _get(field: str, default=None):
            val = raw_data.get(field.encode())
            if val is None:
                return default
            return self._unpack(val)

        return SessionData(
            bot_id=_get("bot_id", 0),
            dc_id=_get("dc_id", 2),
            server_address=_get("server_address", "149.154.167.51"),
            port=_get("port", 443),
            api_id=_get("api_id"),
            test_mode=_get("test_mode", False),
            auth_key=_get("auth_key"),
            date=_get("date", 0),
            user_id=_get("user_id"),
            is_bot=_get("is_bot"),
        )

    # --- Field accessors ---

    async def get_session_field(self, bot_id: int, field: str) -> Any:
        val = await self._redis.hget(self._session_key(bot_id), field.encode())
        if val is None:
            return None
        return self._unpack(val)

    async def set_session_field(self, bot_id: int, field: str, value: Any) -> None:
        await self._redis.hset(
            self._session_key(bot_id),
            field.encode(),
            self._pack(value),
        )

    # --- Peers ---

    async def update_peers(self, bot_id: int, peers: List[Tuple[int, int, str, str]]) -> None:
        if not peers:
            return
        key = self._peers_key(bot_id)
        now = int(time.time())
        mapping = {}
        for peer_id, access_hash, peer_type, phone_number in peers:
            mapping[str(peer_id).encode()] = self._pack(
                (peer_id, access_hash, peer_type, phone_number, now)
            )
        await self._redis.hset(key, mapping=mapping)

    async def update_usernames(self, bot_id: int, usernames: List[Tuple[int, list]]) -> None:
        if not usernames:
            return
        key = self._usernames_key(bot_id)
        mapping = {}
        for peer_id, unames in usernames:
            for uname in unames:
                mapping[uname.lower().encode()] = self._pack(peer_id)
        await self._redis.hset(key, mapping=mapping)

    async def get_peer_by_id(self, bot_id: int, peer_id: int) -> Optional[tuple]:
        val = await self._redis.hget(self._peers_key(bot_id), str(peer_id).encode())
        if val is None:
            return None
        data = self._unpack(val)
        # Return (peer_id, access_hash, type, phone_number, last_update_on)
        return tuple(data)

    async def get_peer_by_username(self, bot_id: int, username: str) -> Optional[tuple]:
        pid_raw = await self._redis.hget(
            self._usernames_key(bot_id), username.lower().encode()
        )
        if pid_raw is None:
            return None
        peer_id = self._unpack(pid_raw)
        return await self.get_peer_by_id(bot_id, peer_id)

    async def get_peer_by_phone_number(self, bot_id: int, phone: str) -> Optional[tuple]:
        # Scan all peers for matching phone (not ideal, but matches SQLite behavior)
        all_peers = await self._redis.hgetall(self._peers_key(bot_id))
        for _, val in all_peers.items():
            data = self._unpack(val)
            if len(data) >= 4 and data[3] == phone:
                return tuple(data)
        return None

    # --- Update state ---

    async def update_state(self, bot_id: int, value=object) -> Any:
        key = self._ustate_key(bot_id)

        if value is object:
            # Read all states
            raw_data = await self._redis.hgetall(key)
            if not raw_data:
                return []
            states = []
            for _, v in raw_data.items():
                states.append(tuple(self._unpack(v)))
            states.sort(key=lambda s: s[3] if s[3] is not None else 0)
            return states

        if isinstance(value, int):
            # Delete state by id
            await self._redis.hdel(key, str(value).encode())
            return

        if isinstance(value, (tuple, list)):
            state_id = value[0]
            # Read existing to merge
            existing_raw = await self._redis.hget(key, str(state_id).encode())
            if existing_raw is not None:
                existing = list(self._unpack(existing_raw))
                new_val = list(value)
                # Merge: keep existing values for None fields
                for i in range(len(new_val)):
                    if new_val[i] is not None:
                        existing[i] = new_val[i]
                value = tuple(existing)

            await self._redis.hset(key, str(state_id).encode(), self._pack(value))

    # --- Migration ---

    async def migrate_from_file(self, session_file: str, bot_id: int) -> Optional[SessionData]:
        """Migrate a per-bot SQLite session file into Redis."""
        import sqlite3

        try:
            conn = sqlite3.connect(session_file)
        except Exception:
            return None

        try:
            cursor = conn.cursor()

            # Read session
            cursor.execute("SELECT * FROM sessions LIMIT 1")
            row = cursor.fetchone()
            if row is None:
                return None

            data = SessionData(
                bot_id=bot_id,
                dc_id=row[0],
                server_address=row[2],
                port=row[3],
                api_id=row[1] if len(row) > 1 else None,
                test_mode=bool(row[4]) if len(row) > 4 else False,
                auth_key=row[5] if len(row) > 5 else None,
                date=row[6] if len(row) > 6 else 0,
                user_id=row[7] if len(row) > 7 else None,
                is_bot=bool(row[8]) if len(row) > 8 else None,
            )

            await self.save_session(data)

            # Migrate peers
            try:
                cursor.execute("SELECT id, access_hash, type, phone_number FROM peers")
                peers = []
                for pr in cursor.fetchall():
                    peers.append((pr[0], pr[1], pr[2], pr[3]))
                if peers:
                    await self.update_peers(bot_id, peers)
            except sqlite3.OperationalError:
                pass

            # Migrate usernames
            try:
                cursor.execute("SELECT peer_id, username FROM usernames")
                username_map = {}
                for pr in cursor.fetchall():
                    username_map.setdefault(pr[0], []).append(pr[1])
                if username_map:
                    await self.update_usernames(
                        bot_id,
                        [(pid, unames) for pid, unames in username_map.items()]
                    )
            except sqlite3.OperationalError:
                pass

            # Migrate update_state
            try:
                cursor.execute("SELECT id, pts, qts, date, seq FROM update_state")
                for row in cursor.fetchall():
                    await self.update_state(bot_id, tuple(row))
            except sqlite3.OperationalError:
                pass

            return data
        finally:
            conn.close()
