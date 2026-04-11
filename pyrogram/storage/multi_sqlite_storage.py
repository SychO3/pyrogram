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
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

import aiosqlite

from pyrogram import raw, utils
from .session_data import SessionData
from .sqlite_storage import PROD, get_input_peer

log = logging.getLogger(__name__)

MULTI_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions
(
    bot_id         INTEGER PRIMARY KEY,
    dc_id          INTEGER NOT NULL DEFAULT 2,
    server_address TEXT NOT NULL DEFAULT '149.154.167.51',
    port           INTEGER NOT NULL DEFAULT 443,
    api_id         INTEGER,
    test_mode      INTEGER NOT NULL DEFAULT 0,
    auth_key       BLOB,
    date           INTEGER NOT NULL DEFAULT 0,
    user_id        INTEGER,
    is_bot         INTEGER
);

CREATE TABLE IF NOT EXISTS peers
(
    bot_id         INTEGER NOT NULL,
    peer_id        INTEGER NOT NULL,
    access_hash    INTEGER,
    type           TEXT NOT NULL,
    phone_number   TEXT,
    last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER)),
    PRIMARY KEY (bot_id, peer_id)
);

CREATE TABLE IF NOT EXISTS usernames
(
    bot_id   INTEGER NOT NULL,
    peer_id  INTEGER NOT NULL,
    username TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS update_state
(
    bot_id INTEGER NOT NULL,
    id     INTEGER NOT NULL,
    pts    INTEGER,
    qts    INTEGER,
    date   INTEGER,
    seq    INTEGER,
    PRIMARY KEY (bot_id, id)
);

CREATE TABLE IF NOT EXISTS version
(
    number INTEGER PRIMARY KEY
);

CREATE INDEX IF NOT EXISTS idx_peers_phone ON peers (bot_id, phone_number);
CREATE INDEX IF NOT EXISTS idx_usernames_botid ON usernames (bot_id, peer_id);
CREATE INDEX IF NOT EXISTS idx_usernames_username ON usernames (bot_id, username);
"""

VERSION = 1
BATCH_SIZE = 100


class MultiSQLiteStorage:
    """Unified WAL SQLite database with per-bot partitioned storage.

    All bots share a single database file. Tables are keyed by bot_id.
    Writes go through an async batch writer for throughput.
    """

    def __init__(self, path: str, wal_autocheckpoint: int = 1000):
        self.path = path
        self.wal_autocheckpoint = wal_autocheckpoint
        self.conn: Optional[aiosqlite.Connection] = None
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._writer_task: Optional[asyncio.Task] = None
        self._closed = False

    async def open(self) -> None:
        self.conn = await aiosqlite.connect(self.path, timeout=10)
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute(f"PRAGMA wal_autocheckpoint={self.wal_autocheckpoint}")
        await self.conn.execute("PRAGMA busy_timeout=5000")
        await self.conn.execute("PRAGMA foreign_keys=ON")
        await self.conn.executescript(MULTI_SCHEMA)

        # Check/set version
        async with self.conn.execute("SELECT number FROM version") as cur:
            row = await cur.fetchone()
        if row is None:
            await self.conn.execute("INSERT INTO version VALUES (?)", (VERSION,))
            await self.conn.commit()

        self._closed = False
        self._writer_task = asyncio.get_event_loop().create_task(self._writer_loop())

    async def close(self) -> None:
        self._closed = True
        if self._writer_task and not self._writer_task.done():
            # Drain remaining writes
            await self._write_queue.put(None)  # sentinel
            await self._writer_task
        if self.conn:
            await self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            await self.conn.close()
            self.conn = None

    async def _writer_loop(self) -> None:
        while True:
            batch = []
            # Block on first item
            item = await self._write_queue.get()
            if item is None:
                # Drain any remaining
                while not self._write_queue.empty():
                    item = self._write_queue.get_nowait()
                    if item is not None:
                        batch.append(item)
                if batch:
                    await self._execute_batch(batch)
                return
            batch.append(item)

            # Drain up to BATCH_SIZE
            while len(batch) < BATCH_SIZE and not self._write_queue.empty():
                item = self._write_queue.get_nowait()
                if item is None:
                    # Process remaining batch, then exit
                    await self._execute_batch(batch)
                    return
                batch.append(item)

            await self._execute_batch(batch)

    async def _execute_batch(self, batch: list) -> None:
        try:
            for sql, params in batch:
                await self.conn.execute(sql, params)
            await self.conn.commit()
        except Exception:
            # Batch failed, retry individually
            for sql, params in batch:
                try:
                    await self.conn.execute(sql, params)
                    await self.conn.commit()
                except Exception:
                    log.exception("Write failed: %s %s", sql, params)

    def _enqueue_write(self, sql: str, params: tuple = ()) -> None:
        if self._closed:
            raise RuntimeError("Storage is closed")
        self._write_queue.put_nowait((sql, params))

    # --- Session operations ---

    async def read_session(self, bot_id: int) -> Optional[SessionData]:
        async with self.conn.execute(
            "SELECT bot_id, dc_id, server_address, port, api_id, test_mode, "
            "auth_key, date, user_id, is_bot FROM sessions WHERE bot_id = ?",
            (bot_id,),
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            return None
        return SessionData(
            bot_id=row[0],
            dc_id=row[1],
            server_address=row[2],
            port=row[3],
            api_id=row[4],
            test_mode=bool(row[5]),
            auth_key=row[6],
            date=row[7],
            user_id=row[8],
            is_bot=bool(row[9]) if row[9] is not None else None,
        )

    async def save_session(self, data: SessionData) -> None:
        self._enqueue_write(
            "REPLACE INTO sessions (bot_id, dc_id, server_address, port, api_id, "
            "test_mode, auth_key, date, user_id, is_bot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data.bot_id,
                data.dc_id,
                data.server_address,
                data.port,
                data.api_id,
                int(data.test_mode),
                data.auth_key,
                data.date,
                data.user_id,
                int(data.is_bot) if data.is_bot is not None else None,
            ),
        )

    async def read_all_sessions(self) -> list[SessionData]:
        async with self.conn.execute(
            "SELECT bot_id, dc_id, server_address, port, api_id, test_mode, "
            "auth_key, date, user_id, is_bot FROM sessions"
        ) as cur:
            rows = await cur.fetchall()
        return [
            SessionData(
                bot_id=r[0], dc_id=r[1], server_address=r[2], port=r[3],
                api_id=r[4], test_mode=bool(r[5]), auth_key=r[6], date=r[7],
                user_id=r[8], is_bot=bool(r[9]) if r[9] is not None else None,
            )
            for r in rows
        ]

    async def delete_session(self, bot_id: int) -> None:
        self._enqueue_write("DELETE FROM sessions WHERE bot_id = ?", (bot_id,))
        self._enqueue_write("DELETE FROM peers WHERE bot_id = ?", (bot_id,))
        self._enqueue_write("DELETE FROM usernames WHERE bot_id = ?", (bot_id,))
        self._enqueue_write("DELETE FROM update_state WHERE bot_id = ?", (bot_id,))

    # --- Session field accessors (for Storage ABC compat in BotHandle) ---

    async def get_session_field(self, bot_id: int, field: str) -> Any:
        async with self.conn.execute(
            f"SELECT {field} FROM sessions WHERE bot_id = ?", (bot_id,)
        ) as cur:
            row = await cur.fetchone()
        return row[0] if row else None

    async def ensure_session_row(self, bot_id: int) -> None:
        """Insert a default session row for *bot_id* if one does not exist."""
        await self.conn.execute(
            "INSERT OR IGNORE INTO sessions (bot_id) VALUES (?)", (bot_id,)
        )
        await self.conn.commit()

    async def set_session_field(self, bot_id: int, field: str, value: Any) -> None:
        await self.conn.execute(
            f"UPDATE sessions SET {field} = ? WHERE bot_id = ?", (value, bot_id)
        )
        await self.conn.commit()

    # --- Peer operations ---

    async def update_peers(
        self, bot_id: int, peers: List[Tuple[int, int, str, str]]
    ) -> None:
        for peer_id, access_hash, peer_type, phone_number in peers:
            self._enqueue_write(
                "REPLACE INTO peers (bot_id, peer_id, access_hash, type, phone_number) "
                "VALUES (?, ?, ?, ?, ?)",
                (bot_id, peer_id, access_hash, peer_type, phone_number),
            )

    async def update_usernames(
        self, bot_id: int, usernames: List[Tuple[int, List[str]]]
    ) -> None:
        for peer_id, _ in usernames:
            self._enqueue_write(
                "DELETE FROM usernames WHERE bot_id = ? AND peer_id = ?",
                (bot_id, peer_id),
            )
        for peer_id, names in usernames:
            for name in names:
                self._enqueue_write(
                    "INSERT INTO usernames (bot_id, peer_id, username) VALUES (?, ?, ?)",
                    (bot_id, peer_id, name),
                )

    async def get_peer_by_id(self, bot_id: int, peer_id: int):
        async with self.conn.execute(
            "SELECT peer_id, access_hash, type FROM peers "
            "WHERE bot_id = ? AND peer_id = ?",
            (bot_id, peer_id),
        ) as cur:
            r = await cur.fetchone()
        if r is None:
            raise KeyError(f"ID not found: {peer_id}")
        return get_input_peer(*r)

    async def get_peer_by_username(self, bot_id: int, username: str):
        async with self.conn.execute(
            "SELECT p.peer_id, p.access_hash, p.type, p.last_update_on FROM peers p "
            "JOIN usernames u ON p.bot_id = u.bot_id AND p.peer_id = u.peer_id "
            "WHERE p.bot_id = ? AND u.username = ? "
            "ORDER BY p.last_update_on DESC",
            (bot_id, username),
        ) as cur:
            r = await cur.fetchone()
        if r is None:
            raise KeyError(f"Username not found: {username}")
        if abs(time.time() - r[3]) > 8 * 60 * 60:
            raise KeyError(f"Username expired: {username}")
        return get_input_peer(*r[:3])

    async def get_peer_by_phone_number(self, bot_id: int, phone_number: str):
        async with self.conn.execute(
            "SELECT peer_id, access_hash, type FROM peers "
            "WHERE bot_id = ? AND phone_number = ?",
            (bot_id, phone_number),
        ) as cur:
            r = await cur.fetchone()
        if r is None:
            raise KeyError(f"Phone number not found: {phone_number}")
        return get_input_peer(*r)

    # --- Update state ---

    async def update_state(self, bot_id: int, value: Any = object):
        if value is object:
            async with self.conn.execute(
                "SELECT id, pts, qts, date, seq FROM update_state "
                "WHERE bot_id = ? ORDER BY date ASC",
                (bot_id,),
            ) as cur:
                return await cur.fetchall()
        elif isinstance(value, int):
            self._enqueue_write(
                "DELETE FROM update_state WHERE bot_id = ? AND id = ?",
                (bot_id, value),
            )
        else:
            id_, pts, qts, date, seq = value
            self._enqueue_write(
                "REPLACE INTO update_state (bot_id, id, pts, qts, date, seq) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (bot_id, id_, pts, qts, date, seq),
            )

    # --- Migration from per-bot SQLite file ---

    async def migrate_from_file(self, session_file: str, bot_id: int) -> Optional[SessionData]:
        path = Path(session_file)
        if not path.is_file():
            return None

        old_conn = await aiosqlite.connect(str(path), timeout=10)
        try:
            # Read session
            async with old_conn.execute(
                "SELECT dc_id, server_address, port, api_id, test_mode, "
                "auth_key, date, user_id, is_bot FROM sessions"
            ) as cur:
                row = await cur.fetchone()

            if row is None:
                return None

            data = SessionData(
                bot_id=bot_id,
                dc_id=row[0],
                server_address=row[1] or PROD.get(row[0], "149.154.167.51"),
                port=row[2] or 443,
                api_id=row[3],
                test_mode=bool(row[4]),
                auth_key=row[5],
                date=row[6],
                user_id=row[7],
                is_bot=bool(row[8]) if row[8] is not None else None,
            )
            await self.save_session(data)

            # Migrate peers
            async with old_conn.execute(
                "SELECT id, access_hash, type, phone_number FROM peers"
            ) as cur:
                peers = await cur.fetchall()
            if peers:
                await self.update_peers(
                    bot_id, [(r[0], r[1], r[2], r[3]) for r in peers]
                )

            # Migrate usernames
            async with old_conn.execute(
                "SELECT id, username FROM usernames"
            ) as cur:
                uname_rows = await cur.fetchall()
            if uname_rows:
                # Group by peer_id
                unames: dict[int, list[str]] = {}
                for peer_id, username in uname_rows:
                    unames.setdefault(peer_id, []).append(username)
                await self.update_usernames(
                    bot_id, [(pid, names) for pid, names in unames.items()]
                )

            # Migrate update_state
            async with old_conn.execute(
                "SELECT id, pts, qts, date, seq FROM update_state"
            ) as cur:
                states = await cur.fetchall()
            for state in states:
                await self.update_state(bot_id, state)

            return data
        finally:
            await old_conn.close()
