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
from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from pyrogram import __version__, raw, utils
from pyrogram.storage import Storage
from pyrogram.update_state import UpdateState

if TYPE_CHECKING:
    from pyrogram.connection import Connection
    from pyrogram.connection.transport import TCP
    from pyrogram.runtime import Runtime
    from pyrogram.session import Session
    from pyrogram.storage import MultiSQLiteStorage

log = logging.getLogger(__name__)


@dataclass
class BotConfig:
    api_id: int
    api_hash: str = ""
    app_version: str = f"Pyrogram {__version__}"
    device_model: str = ""
    system_version: str = ""
    system_lang_code: str = "en"
    lang_pack: str = ""
    lang_code: str = "en"
    init_connection_params: Any = None
    no_updates: bool = False
    skip_updates: bool = False
    sleep_threshold: float = 10.0
    max_concurrent_transmissions: int = 3

    def __post_init__(self):
        if not self.device_model:
            import platform
            self.device_model = f"{platform.python_implementation()} {platform.python_version()}"
        if not self.system_version:
            import platform
            self.system_version = f"{platform.system()} {platform.release()}"


class BotStorageProxy(Storage):
    """Proxy that adds bot_id to all storage calls for Storage ABC compatibility.

    When owns_storage=True (standalone Client mode), open()/close() manage
    the underlying MultiSQLiteStorage lifecycle. When False (Runtime mode),
    those are no-ops since Runtime manages the storage.
    """

    def __init__(self, storage: "MultiSQLiteStorage", bot_id: int, owns_storage: bool = False):
        super().__init__(str(bot_id))
        self._storage = storage
        self._bot_id = bot_id
        self._owns_storage = owns_storage

    async def api_id(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "api_id")
        await self._storage.set_session_field(self._bot_id, "api_id", value)

    async def dc_id(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "dc_id")
        await self._storage.set_session_field(self._bot_id, "dc_id", value)

    async def server_address(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "server_address")
        await self._storage.set_session_field(self._bot_id, "server_address", value)

    async def port(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "port")
        await self._storage.set_session_field(self._bot_id, "port", value)

    async def test_mode(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "test_mode")
        await self._storage.set_session_field(self._bot_id, "test_mode", value)

    async def auth_key(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "auth_key")
        await self._storage.set_session_field(self._bot_id, "auth_key", value)

    async def date(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "date")
        await self._storage.set_session_field(self._bot_id, "date", value)

    async def user_id(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "user_id")
        await self._storage.set_session_field(self._bot_id, "user_id", value)

    async def is_bot(self, value=object):
        if value is object:
            return await self._storage.get_session_field(self._bot_id, "is_bot")
        await self._storage.set_session_field(self._bot_id, "is_bot", value)

    async def update_peers(self, peers: List[Tuple[int, int, str, str]]) -> None:
        await self._storage.update_peers(self._bot_id, peers)

    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        await self._storage.update_usernames(self._bot_id, usernames)

    async def update_state(self, value=object):
        return await self._storage.update_state(self._bot_id, value)

    async def get_peer_by_id(self, peer_id: int):
        return await self._storage.get_peer_by_id(self._bot_id, peer_id)

    async def get_peer_by_username(self, username: str):
        return await self._storage.get_peer_by_username(self._bot_id, username)

    async def get_peer_by_phone_number(self, phone_number: str):
        return await self._storage.get_peer_by_phone_number(self._bot_id, phone_number)

    async def open(self):
        if self._owns_storage:
            await self._storage.open()
        await self._storage.ensure_session_row(self._bot_id)

    async def save(self):
        pass

    async def close(self):
        if self._owns_storage:
            await self._storage.close()

    async def delete(self):
        await self._storage.delete_session(self._bot_id)


class BotHandle:
    """Per-bot state object. Provides the same interface as Client for Session compatibility.

    Session code references ``self.client.*`` extensively. BotHandle implements
    the same attributes so Session works with either Client or BotHandle.
    """

    def __init__(
        self,
        runtime: "Runtime",
        bot_id: int,
        config: BotConfig,
        auth_key: bytes,
    ):
        from hashlib import sha1
        self._runtime = runtime
        self.bot_id = bot_id
        self.config = config

        # Auth key
        self.auth_key = auth_key
        self.auth_key_id = sha1(auth_key).digest()[-8:] if auth_key else b""

        # Server time tracking (per-bot)
        self._server_time_offset = 0.0

        # Storage proxy
        self.storage = BotStorageProxy(runtime.storage, bot_id)

        # Session references
        self.session: Optional["Session"] = None
        self.sessions: dict = {}
        self.media_sessions: dict = {}
        self.sessions_lock = asyncio.Lock()
        self._session_futures: dict = {}

        # File transfer semaphores
        self.save_file_semaphore = asyncio.Semaphore(config.max_concurrent_transmissions)
        self.get_file_semaphore = asyncio.Semaphore(config.max_concurrent_transmissions)

        # Handlers
        self.connect_handler: Optional[Callable] = None
        self.disconnect_handler: Optional[Callable] = None

        # Name for logging
        self.name = str(bot_id)

        # Update state tracker (pts/qts/seq gap detection)
        self._update_state = UpdateState(bot_id=bot_id)

        # ipv6 detection for Auth compatibility
        self.ipv6 = False

        # skip_updates for recover_gaps compatibility
        self.skip_updates = config.skip_updates

    # --- Properties delegated to Runtime ---

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._runtime.loop

    @property
    def proxy(self):
        return self._runtime.proxy

    @property
    def connection_factory(self):
        return self._runtime.connection_factory

    @property
    def protocol_factory(self):
        return self._runtime.protocol_factory

    @property
    def executor(self):
        return self._runtime.handler_executor

    @property
    def crypto_executor(self):
        return self._runtime.crypto_executor

    # --- Properties delegated to Session (MTProto per-session state) ---

    @property
    def server_salt(self) -> int:
        return self.session.salt if self.session else 0

    @property
    def session_id(self) -> bytes:
        return self.session.session_id if self.session else b""

    @property
    def msg_factory(self):
        return self.session.msg_factory if self.session else None

    @property
    def pending_results(self) -> dict:
        return self.session.results if self.session else {}

    @property
    def stored_msg_ids(self) -> list:
        return self.session.stored_msg_ids if self.session else []

    # --- Properties from config ---

    @property
    def app_version(self) -> str:
        return self.config.app_version

    @property
    def device_model(self) -> str:
        return self.config.device_model

    @property
    def system_version(self) -> str:
        return self.config.system_version

    @property
    def system_lang_code(self) -> str:
        return self.config.system_lang_code

    @property
    def lang_pack(self) -> str:
        return self.config.lang_pack

    @property
    def lang_code(self) -> str:
        return self.config.lang_code

    @property
    def init_connection_params(self):
        return self.config.init_connection_params

    @property
    def no_updates(self) -> bool:
        return self.config.no_updates

    @property
    def sleep_threshold(self) -> float:
        return self.config.sleep_threshold

    # --- Server time ---

    @property
    def server_time(self) -> float:
        return time.time() + self._server_time_offset

    def _set_server_time(self, msg_id: int):
        server_ts = msg_id / float(2**32)
        self._server_time_offset = server_ts - time.time()

    # --- Update state ---

    @property
    def update_state(self) -> UpdateState:
        return self._update_state

    async def load_update_state(self) -> None:
        await self._update_state.load_from_storage(self.storage)

    async def save_update_state(self) -> None:
        await self._update_state.save_to_storage(self.storage)

    # --- Update handling ---

    async def handle_updates(self, raw_update) -> None:
        if self._runtime.update_dispatcher is None:
            return

        self._runtime.metrics.record_update()

        gap_detected = False

        if isinstance(raw_update, (raw.types.Updates, raw.types.UpdatesCombined)):
            await self.fetch_peers(raw_update.users)
            await self.fetch_peers(raw_update.chats)

            users = {u.id: u for u in raw_update.users}
            chats = {c.id: c for c in raw_update.chats}

            # Apply seq gap detection
            if hasattr(raw_update, "seq") and raw_update.seq:
                seq_start = getattr(raw_update, "seq_start", None) or raw_update.seq
                if self._update_state.apply_seq(raw_update.seq, seq_start):
                    gap_detected = True

            for update in raw_update.updates:
                # Apply pts/qts gap detection
                pts = getattr(update, "pts", None)
                pts_count = getattr(update, "pts_count", None)
                qts = getattr(update, "qts", None)

                if pts is not None and pts_count is not None:
                    channel_id = getattr(update, "channel_id", 0) or 0
                    entity_id = utils.get_channel_id(channel_id) if channel_id else 0
                    if self._update_state.apply_pts(
                        entity_id, pts, pts_count,
                        date=getattr(raw_update, "date", None),
                    ):
                        gap_detected = True

                if qts is not None:
                    if self._update_state.apply_qts(qts):
                        gap_detected = True

                await self._runtime.update_dispatcher.dispatch(
                    self.bot_id, (update, users, chats)
                )
        elif isinstance(raw_update, raw.types.UpdateShort):
            # Apply pts/qts gap detection for short updates
            update = raw_update.update
            pts = getattr(update, "pts", None)
            pts_count = getattr(update, "pts_count", None)
            qts = getattr(update, "qts", None)

            if pts is not None and pts_count is not None:
                channel_id = getattr(update, "channel_id", 0) or 0
                entity_id = utils.get_channel_id(channel_id) if channel_id else 0
                if self._update_state.apply_pts(entity_id, pts, pts_count):
                    gap_detected = True

            if qts is not None:
                if self._update_state.apply_qts(qts):
                    gap_detected = True

            await self._runtime.update_dispatcher.dispatch(
                self.bot_id, (update, {}, {})
            )
        elif isinstance(raw_update, (raw.types.UpdateShortMessage, raw.types.UpdateShortChatMessage)):
            # These carry pts directly
            pts = getattr(raw_update, "pts", None)
            pts_count = getattr(raw_update, "pts_count", None)
            if pts is not None and pts_count is not None:
                if self._update_state.apply_pts(0, pts, pts_count):
                    gap_detected = True

            await self._runtime.update_dispatcher.dispatch(self.bot_id, raw_update)
        else:
            await self._runtime.update_dispatcher.dispatch(self.bot_id, raw_update)

        # Trigger gap recovery asynchronously if gaps were detected
        if gap_detected and not self.skip_updates:
            asyncio.create_task(self._recover_gaps())

    # --- Gap recovery ---

    async def _recover_gaps(self) -> None:
        """Trigger gap recovery via UpdateState.fill_gap, guarded by a lock."""
        if not hasattr(self, '_gap_lock'):
            self._gap_lock = asyncio.Lock()

        if self._gap_lock.locked():
            # Already recovering, skip
            return

        async with self._gap_lock:
            try:
                await self._update_state.fill_gap(self)
            except Exception:
                log.exception("Bot %d: gap recovery failed", self.bot_id)

    # --- Media / CDN session management ---

    async def get_media_session(self, dc_id: int) -> "Session":
        """Get or create a media session for the given DC.

        Media sessions reuse the auth key from the main (non-media) session
        to the same DC. If no auth key exists for that DC, performs
        ExportAuthorization + ImportAuthorization.
        """
        from pyrogram.session import Session

        # Check existing
        async with self.sessions_lock:
            existing = self.media_sessions.get(dc_id)
            if existing is not None:
                return existing

            # Check pending creation
            session_key = (dc_id, True)
            pending = self._session_futures.get(session_key)
            if pending is not None:
                return await pending

            future = self.loop.create_future()
            future.add_done_callback(lambda f: None if f.cancelled() else f.exception())
            self._session_futures[session_key] = future

        try:
            # Get auth key from non-media session to same DC
            non_media = self.sessions.get(dc_id)
            if non_media is not None:
                auth_key = non_media.auth_key
            elif self.session is not None:
                # Create auth key for the DC
                dc_id_main = await self.storage.dc_id()
                if dc_id == dc_id_main:
                    auth_key = self.auth_key
                else:
                    auth_key = await self._runtime.create_auth_key(
                        self, dc_id,
                        await self.storage.server_address(),
                        await self.storage.port(),
                        bool(await self.storage.test_mode()),
                    )
            else:
                raise ConnectionError("No main session available for media session creation")

            session = Session(
                client=self,
                dc_id=dc_id,
                server_address=await self.storage.server_address(),
                port=await self.storage.port(),
                auth_key=auth_key,
                test_mode=bool(await self.storage.test_mode()),
                is_media=True,
            )

            await session.start()

            try:
                await asyncio.wait_for(session.is_started.wait(), Session.WAIT_TIMEOUT)
            except asyncio.TimeoutError:
                with suppress(Exception):
                    await session.stop()
                raise ConnectionError(f"Media session start timed out for DC{dc_id}")

            # Export/Import authorization if not current DC
            dc_id_main = await self.storage.dc_id()
            if dc_id != dc_id_main and self.session is not None:
                for _ in range(3):
                    try:
                        exported = await self.session.invoke(
                            raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                        )
                        await session.invoke(
                            raw.functions.auth.ImportAuthorization(
                                id=exported.id, bytes=exported.bytes
                            )
                        )
                        break
                    except Exception:
                        continue

            async with self.sessions_lock:
                self.media_sessions[dc_id] = session
                pending = self._session_futures.pop(session_key, None)
                if pending is not None and not pending.done():
                    pending.set_result(session)

            # Register with ConnectionManager
            if self._runtime.connection_mgr is not None:
                await self._runtime.connection_mgr.register_session(
                    self.bot_id, dc_id, session
                )
                self._runtime.metrics.record_connection_create(dc_id)

            return session

        except Exception as e:
            async with self.sessions_lock:
                pending = self._session_futures.pop(session_key, None)
                if pending is not None and not pending.done():
                    pending.set_exception(e)
            raise

    async def stop_media_sessions(self) -> None:
        """Stop all media sessions for this bot."""
        async with self.sessions_lock:
            sessions_to_stop = list(self.media_sessions.values())
            self.media_sessions.clear()

        for session in sessions_to_stop:
            try:
                await session.stop()
            except Exception as e:
                log.debug("Error stopping media session: %s", e)

    # --- Connection lost callback ---

    async def on_connection_lost(self, dc_id: int) -> None:
        """Called when a connection to a DC is lost.

        Records the event in RuntimeMetrics and lets Session.restart()
        handle the actual reconnection.
        """
        self._runtime.metrics.record_reconnect()
        log.info("Bot %d: connection lost to DC%d", self.bot_id, dc_id)

        # Notify ConnectionManager for DC-level coordination
        await self._runtime.on_bot_connection_lost(self.bot_id, dc_id)

    # --- Peer fetching (mirrors Client.fetch_peers) ---

    async def fetch_peers(self, peers) -> bool:
        is_min = False
        parsed_peers = []
        parsed_usernames = []

        for peer in peers:
            if getattr(peer, "min", False) and not isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                is_min = True
                continue

            usernames = []
            peer_id = access_hash = phone_number = None
            peer_type = ""

            if isinstance(peer, raw.types.User):
                peer_id = peer.id
                access_hash = peer.access_hash
                phone_number = peer.phone
                peer_type = "bot" if peer.bot else "user"

                if peer.usernames:
                    usernames.extend(u.username.lower() for u in peer.usernames)
                elif peer.username:
                    usernames.append(peer.username.lower())
            elif isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                peer_id = -peer.id
                access_hash = 0
                peer_type = "group"
            elif isinstance(peer, raw.types.Channel):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = (
                    "direct" if peer.monoforum else
                    "channel" if peer.broadcast else
                    "forum" if peer.forum else
                    "supergroup"
                )
                if peer.usernames:
                    usernames.extend(u.username.lower() for u in peer.usernames)
                elif peer.username:
                    usernames.append(peer.username.lower())
            elif isinstance(peer, raw.types.ChannelForbidden):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"
            else:
                continue

            parsed_peers.append((peer_id, access_hash, peer_type, phone_number))
            if usernames:
                parsed_usernames.append((peer_id, usernames))

        await self.storage.update_peers(parsed_peers)
        if parsed_usernames:
            await self.storage.update_usernames(parsed_usernames)

        return is_min

    # --- Invoke (delegates to main session) ---

    async def invoke(self, query, *args, **kwargs):
        if self.session is None:
            raise ConnectionError("Bot is not connected")
        return await self.session.invoke(query, *args, **kwargs)

    def __repr__(self) -> str:
        return f"BotHandle(bot_id={self.bot_id})"
