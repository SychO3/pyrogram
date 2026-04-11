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
import bisect
import logging
import os
import inspect
from enum import Enum, auto
from hashlib import sha1
from io import BytesIO
from typing import Any, Dict, List, Optional, Set, Union

import pyrogram
from pyrogram import raw, utils
from pyrogram.connection import Connection
from pyrogram.crypto import mtproto
from pyrogram.errors import (
    AuthKeyDuplicated,
    BadMsgNotification,
    FloodPremiumWaitX,
    FloodWaitX,
    InternalServerError,
    RPCError,
    SecurityCheckMismatch,
    ServiceUnavailable,
    Unauthorized,
)
from pyrogram.raw.all import layer
from pyrogram.raw.core import FutureSalts, Int, MsgContainer, TLObject

from .internals import MsgFactory

log = logging.getLogger(__name__)


class SessionState(Enum):
    STARTING = auto()
    STARTED = auto()
    STOPPING = auto()
    STOPPED = auto()


class TransportError(Exception):
    pass


class AuthKeyNotFound(TransportError):
    pass


class TransportFlood(TransportError):
    pass


class InvalidDC(TransportError):
    pass


class Result:
    __slots__ = ("value", "event")

    def __init__(self):
        self.value: Any = None
        self.event: asyncio.Event = asyncio.Event()


class Session:
    START_TIMEOUT = 2
    WAIT_TIMEOUT = 15
    SLEEP_THRESHOLD = 10
    MAX_RETRIES = 10
    ACKS_THRESHOLD = 10
    PING_INTERVAL = 5
    RETRY_DELAY = 1
    MAX_RESTART_DELAY = 10
    STORED_MSG_IDS_MAX_SIZE = 1000 * 2
    CRYPTO_EXECUTOR_WORKERS = min(4, os.cpu_count() or 2)
    MAX_CONSECUTIVE_IGNORED = 30
    MAX_CONCURRENT_PACKETS = 50

    def __init__(
        self,
        client: Union["pyrogram.Client", Any],
        dc_id: int,
        server_address: str,
        port: int,
        auth_key: bytes,
        test_mode: bool,
        is_media: bool = False,
        is_cdn: bool = False,
    ):
        self.client = client
        self.dc_id = dc_id
        self.server_address = server_address
        self.port = port
        self.auth_key = auth_key
        self.test_mode = test_mode
        self.is_media = is_media
        self.is_cdn = is_cdn

        self.connection: Optional[Connection] = None

        self._state = SessionState.STOPPED
        self._state_lock = asyncio.Lock()

        self.auth_key_id = sha1(auth_key).digest()[-8:]

        self.session_id = os.urandom(8)
        self.msg_factory = MsgFactory(self.client)

        self.salt = 0

        self.ignore_count = 0

        self.pending_acks: Set[int] = set()

        self.results: Dict[int, Result] = {}

        self.stored_msg_ids: List[int] = []
        self.recent_msg_ids: Set[int] = set()

        self.ping_task: Optional[asyncio.Task] = None
        self.ping_task_event = asyncio.Event()

        self.recv_task: Optional[asyncio.Task] = None

        self.is_started = asyncio.Event()
        self.restart_lock = asyncio.Lock()
        self.fatal_error: Optional[BaseException] = None

        self._consecutive_restarts: int = 0
        self._restart_generation: int = 0
        self._packet_semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_PACKETS)

    @property
    def _log_prefix(self) -> str:
        kind = "media" if self.is_media else ("cdn" if self.is_cdn else "main")
        return f"DC{self.dc_id}-{kind}"

    @property
    def state(self) -> SessionState:
        """Get current session state"""
        return self._state

    async def _set_state(self, new_state: SessionState) -> None:
        async with self._state_lock:
            old_state = self._state
            self._state = new_state
            log.debug("[%s] Session state: %s -> %s", self._log_prefix, old_state.name, new_state.name)

    async def start(self) -> None:
        async with self._state_lock:
            if self._state in (SessionState.STARTED, SessionState.STARTING):
                log.debug("[%s] Session already started", self._log_prefix)
                return
            self._state = SessionState.STARTING

        self.fatal_error = None

        self.connection = self.client.connection_factory(
            dc_id=self.dc_id,
            server_address=self.server_address,
            port=self.port,
            test_mode=self.test_mode,
            proxy=self.client.proxy,
            media=self.is_media,
            protocol_factory=self.client.protocol_factory,
            crypto_executor_workers=self.CRYPTO_EXECUTOR_WORKERS,
            loop=self.client.loop,
            crypto_executor=getattr(self.client, 'crypto_executor', None),
        )

        try:
            await self.connection.connect()

            # Wire up quick-ack handler
            if self.connection.protocol is not None:
                self.connection.protocol.quick_ack_handler = self._on_quick_ack

            self.recv_task = self.client.loop.create_task(self.recv_worker())

            await self.send(raw.functions.Ping(ping_id=0), timeout=self.START_TIMEOUT)

            init_connection_params = self.client.init_connection_params

            if isinstance(init_connection_params, dict):
                init_connection_params = utils.obj_to_jsonvalue(init_connection_params)

            if not self.is_cdn:
                await self.send(
                    raw.functions.InvokeWithLayer(
                        layer=layer,
                        query=raw.functions.InitConnection(
                            api_id=await self.client.storage.api_id(),
                            app_version=self.client.app_version,
                            device_model=self.client.device_model,
                            system_version=self.client.system_version,
                            system_lang_code=self.client.system_lang_code,
                            lang_pack=self.client.lang_pack,
                            lang_code=self.client.lang_code,
                            query=raw.functions.help.GetConfig(),
                            params=init_connection_params,
                        )
                    ),
                    timeout=self.START_TIMEOUT
                )

            self.ping_task = self.client.loop.create_task(self.ping_worker())

            log.info(
                "[%s] Session initialized: Pyrogram v%s (Layer %s)",
                self._log_prefix, pyrogram.__version__, layer
            )
            log.info("[%s] Device: %s - %s", self._log_prefix, self.client.device_model, self.client.app_version)
            log.info("[%s] System: %s (%s)", self._log_prefix, self.client.system_version, self.client.lang_code)
        except (AuthKeyDuplicated, Unauthorized):
            await self.stop()
            raise
        except (OSError, RPCError, ConnectionError) as e:
            log.info("[%s] Session start failed: %s - %s", self._log_prefix, e.__class__.__name__, e)
            await self.stop()
            self._schedule_restart("session start failed")
            return
        except Exception:
            await self.stop()
            raise

        await self._set_state(SessionState.STARTED)
        self.is_started.set()
        self._consecutive_restarts = 0

        log.info("[%s] Session started", self._log_prefix)

        await self._invoke_handler(self.client.connect_handler)

    async def stop(self) -> None:
        async with self._state_lock:
            if self._state in (SessionState.STOPPED, SessionState.STOPPING):
                log.debug("[%s] Session already stopped", self._log_prefix)
                return
            self._state = SessionState.STOPPING

        self.is_started.clear()
        self._fail_pending_results(ConnectionError("Session stopped"))

        # Close connection FIRST to break any stuck I/O (e.g. drain() in ping_worker)
        if self.connection is not None:
            await self.connection.close()

        # Cancel tasks after connection is closed so stuck I/O fails immediately
        self.ping_task_event.set()
        await self._cancel_task(self.ping_task)
        self.ping_task = None
        self.ping_task_event.clear()

        await self._cancel_task(self.recv_task)
        self.recv_task = None

        self.ignore_count = 0
        self.stored_msg_ids.clear()
        self.pending_acks.clear()

        await self._set_state(SessionState.STOPPED)

        log.info("[%s] Session stopped", self._log_prefix)

        await self._invoke_handler(self.client.disconnect_handler)

    async def restart(self) -> None:
        # Capture generation BEFORE acquiring the lock (no await in between, so
        # no interleaving in asyncio).  If another restart completes while we
        # wait for the lock, the generation will have advanced and we can skip.
        expected_gen = self._restart_generation

        async with self.restart_lock:
            if self._restart_generation != expected_gen:
                log.debug("[%s] Skipping redundant restart (generation %d -> %d)",
                          self._log_prefix, expected_gen, self._restart_generation)
                return

            if self.stored_msg_ids:
                self.recent_msg_ids = set(self.stored_msg_ids[-30:])

            await self.stop()

            if self._consecutive_restarts > 0:
                delay = min(
                    self.RETRY_DELAY * (2 ** min(self._consecutive_restarts - 1, 5)),
                    self.MAX_RESTART_DELAY
                )
                log.info(
                    "[%s] Restart backoff: %.1fs (attempt #%d)",
                    self._log_prefix, delay, self._consecutive_restarts + 1
                )
                await asyncio.sleep(delay)

            self._consecutive_restarts += 1
            self._restart_generation += 1

            self.session_id = os.urandom(8)
            self.msg_factory = MsgFactory(self.client)

            await self.start()

        # After lock released: sync update state so the server resumes pushing
        # updates on the new session.  Only needed for the main session.
        if self.is_started.is_set() and not self.is_cdn and not self.is_media:
            try:
                await self.send(raw.functions.updates.GetState())
                log.info("[%s] Post-restart update state synced", self._log_prefix)
            except Exception as e:
                log.warning("[%s] Post-restart update sync failed: %s - %s",
                            self._log_prefix, type(e).__name__, e)

    def _fail_pending_results(self, error: BaseException) -> None:
        for result in self.results.values():
            if result.value is None:
                result.value = error
                result.event.set()

    def _set_fatal_error(self, error: BaseException) -> None:
        self.fatal_error = error
        self._fail_pending_results(error)

    @staticmethod
    async def _cancel_task(task: Optional[asyncio.Task]) -> None:
        if task is None or task.done():
            return
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    @staticmethod
    def _parse_transport_error(error_code: int) -> Optional[TransportError]:
        if error_code == 404:
            return AuthKeyNotFound(
                "Auth key not found in the system. Try again or delete your session file "
                "and log in again with your phone number or bot token."
            )
        elif error_code == 429:
            return TransportFlood(
                "Transport flood. Please slow down your requests."
            )
        elif error_code == 444:
            return InvalidDC(
                "Invalid data center. Please check your configuration."
            )
        return None

    def _schedule_restart(self, reason: str = "") -> None:
        """Schedule a restart as a tracked task with error logging."""
        # Notify BotHandle of connection loss for metrics/coordination
        self._notify_connection_lost()

        task = self.client.loop.create_task(self.restart())

        def _on_restart_done(t: asyncio.Task) -> None:
            if t.cancelled():
                return
            exc = t.exception()
            if exc is not None:
                log.error(
                    "[%s] Restart failed (%s): %s - %s",
                    self._log_prefix, reason, type(exc).__name__, exc
                )

        task.add_done_callback(_on_restart_done)
        if reason:
            log.info("[%s] Restart scheduled: %s", self._log_prefix, reason)

    def _notify_connection_lost(self) -> None:
        """Notify BotHandle (if applicable) that this connection was lost."""
        if hasattr(self.client, 'on_connection_lost') and callable(self.client.on_connection_lost):
            self.client.loop.create_task(
                self.client.on_connection_lost(self.dc_id)
            )

    def _on_quick_ack(self, token: bytes) -> None:
        log.debug("[%s] Quick ACK received: %s", self._log_prefix, token.hex())

    async def _invoke_handler(self, handler: Any) -> None:
        if not callable(handler):
            return
        try:
            if inspect.iscoroutinefunction(handler):
                await handler(self.client, self)
            else:
                result = handler(self.client, self)
                if inspect.isawaitable(result):
                    await result
        except Exception as e:
            log.exception(e)

    async def handle_packet(self, packet: bytes) -> None:
        try:
            data = await self.client.loop.run_in_executor(
                self.connection.protocol.crypto_executor,
                mtproto.unpack,
                BytesIO(packet),
                self.session_id,
                self.auth_key,
                self.auth_key_id
            )
        except (ConnectionError, SecurityCheckMismatch, ValueError) as e:
            log.debug(e)
            log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
            self._schedule_restart("security check mismatch")
            return

        messages = (
            data.body.messages
            if isinstance(data.body, MsgContainer)
            else [data]
        )

        log.debug("Received: %s", data)

        for msg in messages:
            if msg.seq_no == 0:
                self.client._set_server_time(msg.msg_id)

            if msg.seq_no % 2 != 0:
                if msg.msg_id in self.pending_acks:
                    continue
                else:
                    self.pending_acks.add(msg.msg_id)

            try:
                if len(self.stored_msg_ids) > Session.STORED_MSG_IDS_MAX_SIZE:
                    del self.stored_msg_ids[:Session.STORED_MSG_IDS_MAX_SIZE // 2]

                if msg.msg_id in self.recent_msg_ids:
                   self.recent_msg_ids.discard(msg.msg_id)
                   raise SecurityCheckMismatch(
                         "The msg_id is belong to most recent closed connection."
                   )

                if self.stored_msg_ids:
                    if msg.msg_id < self.stored_msg_ids[0]:
                        raise SecurityCheckMismatch(
                            "The msg_id is lower than all the stored values"
                        )

                    idx = bisect.bisect_left(self.stored_msg_ids, msg.msg_id)
                    if idx < len(self.stored_msg_ids) and self.stored_msg_ids[idx] == msg.msg_id:
                        raise SecurityCheckMismatch(
                            "The msg_id is equal to any of the stored values"
                        )

                    time_diff = (msg.msg_id - (await self.msg_factory.allocate_message_identity())) / 2 ** 32

                    if time_diff > 30:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 30 seconds in the future. "
                            "Most likely the client time has to be synchronized."
                        )

                    if time_diff < -300:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 300 seconds in the past. "
                            "Most likely the client time has to be synchronized."
                        )

                    self.ignore_count = 0
            except SecurityCheckMismatch as e:
                log.info("Discarding message: %s", e)

                self.ignore_count += 1

                if self.ignore_count >= self.MAX_CONSECUTIVE_IGNORED:
                    log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
                    self.client.loop.create_task(self.restart())
                    return

                continue
            else:
                bisect.insort(self.stored_msg_ids, msg.msg_id)

            if isinstance(msg.body, (raw.types.MsgDetailedInfo, raw.types.MsgNewDetailedInfo)):
                self.pending_acks.add(msg.body.answer_msg_id)
                continue

            if isinstance(msg.body, raw.types.NewSessionCreated):
                continue

            msg_id = None

            if isinstance(msg.body, (raw.types.BadMsgNotification, raw.types.BadServerSalt)):
                msg_id = msg.body.bad_msg_id
            elif isinstance(msg.body, (FutureSalts, raw.types.RpcResult)):
                msg_id = msg.body.req_msg_id
            elif isinstance(msg.body, raw.types.Pong):
                msg_id = msg.body.msg_id
            else:
                if self.client is not None:
                    self.client.loop.create_task(self.client.handle_updates(msg.body))

            if msg_id in self.results:
                self.results[msg_id].value = getattr(msg.body, "result", msg.body)
                self.results[msg_id].event.set()

        if len(self.pending_acks) >= self.ACKS_THRESHOLD:
            log.debug("Sending %s acks", len(self.pending_acks))

            try:
                await self.send(raw.types.MsgsAck(msg_ids=list(self.pending_acks)), False)
            except OSError:
                pass
            else:
                self.pending_acks.clear()

    async def ping_worker(self) -> None:
        log.info("[%s] PingTask started", self._log_prefix)

        while True:
            try:
                await asyncio.wait_for(self.ping_task_event.wait(), self.PING_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            try:
                await self.send(
                    raw.functions.PingDelayDisconnect(
                        ping_id=await self.msg_factory.allocate_message_identity(),
                        disconnect_delay=self.WAIT_TIMEOUT + 10
                    ),
                    wait_response=False
                )

                # Flush pending acks periodically regardless of threshold
                if self.pending_acks:
                    try:
                        await self.send(raw.types.MsgsAck(msg_ids=list(self.pending_acks)), False)
                        self.pending_acks.clear()
                    except OSError:
                        pass
            except (OSError, ConnectionError, TimeoutError) as e:
                log.info("[%s] PingTask triggering restart: %s - %s", self._log_prefix, e.__class__.__name__, e)
                self._schedule_restart("ping failed")
                break
            except RPCError:
                pass

        log.info("[%s] PingTask stopped", self._log_prefix)

    async def _guarded_handle_packet(self, packet: bytes) -> None:
        """Handle a packet with semaphore release guaranteed."""
        try:
            await self.handle_packet(packet)
        finally:
            self._packet_semaphore.release()

    async def recv_worker(self) -> None:
        log.info("[%s] NetworkTask started", self._log_prefix)

        while True:
            try:
                packet = await self.connection.recv()
            except Exception as e:
                log.info("[%s] NetworkTask recv error: %s - %s", self._log_prefix, e.__class__.__name__, e)
                if self.is_started.is_set():
                    self._schedule_restart("recv error")
                break

            if packet is None or len(packet) == 4:
                if packet:
                    error_code = -Int.read(BytesIO(packet))
                    transport_error = self._parse_transport_error(error_code)

                    log.warning(
                        "[%s] Transport error: %s (%s)",
                        self._log_prefix, error_code,
                        transport_error or "unknown error"
                    )

                    if isinstance(transport_error, (AuthKeyNotFound, InvalidDC)):
                        self._set_fatal_error(transport_error)
                        self.client.loop.create_task(self.stop())
                        break

                    if isinstance(transport_error, TransportFlood):
                        await asyncio.sleep(5)

                if self.is_started.is_set():
                    reason = "transport error" if packet else "null packet"
                    self._schedule_restart(reason)

                break

            # Bounded concurrency: wait for semaphore before dispatching
            await self._packet_semaphore.acquire()
            self.client.loop.create_task(self._guarded_handle_packet(packet))

        log.info("[%s] NetworkTask stopped", self._log_prefix)

    async def send(
        self, data: TLObject, wait_response: bool = True, timeout: float = WAIT_TIMEOUT,
        _salt_retries: int = 3
    ) -> Any:
        if self.fatal_error is not None:
            raise self.fatal_error

        message = await self.msg_factory.create(data)
        msg_id = message.msg_id

        if wait_response:
            self.results[msg_id] = Result()

        log.debug("Sent: %s", message)

        try:
            payload = await self.client.loop.run_in_executor(
                self.connection.protocol.crypto_executor,
                mtproto.pack,
                message,
                self.salt,
                self.session_id,
                self.auth_key,
                self.auth_key_id
            )

            await self.connection.send(payload)
        except Exception:
            self.results.pop(msg_id, None)
            raise

        if wait_response:
            try:
                await asyncio.wait_for(self.results[msg_id].event.wait(), timeout)
            except asyncio.TimeoutError:
                pass

            result = self.results.pop(msg_id).value

            if result is None:
                raise TimeoutError("Request timed out")

            if isinstance(result, BaseException):
                raise result

            if isinstance(result, raw.types.RpcError):
                if isinstance(
                    data, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)
                ):
                    data = data.query

                RPCError.raise_it(result, type(data))

            if isinstance(result, raw.types.BadMsgNotification):
                log.warning(
                    "%s: %s", BadMsgNotification.__name__, BadMsgNotification(result.error_code)
                )
                # Error codes 16/17 indicate msg_id too low/high, typically due to time drift
                # after network interruptions or resumed connections.
                if result.error_code in (16, 17):
                    try:
                        await self.restart()
                    except Exception as e:
                        log.info("Restarting session failed due to - %s - %s", e.__class__.__name__, e)
                    # Raise a typed error so invoke() can retry gracefully
                    raise BadMsgNotification(result.error_code)

            if isinstance(result, raw.types.BadServerSalt):
                if _salt_retries <= 0:
                    raise TimeoutError("Too many BadServerSalt responses")
                self.salt = result.new_server_salt
                return await self.send(data, wait_response, timeout, _salt_retries - 1)

            return result

    async def invoke(
        self,
        query: TLObject,
        retries: int = MAX_RETRIES,
        timeout: float = WAIT_TIMEOUT,
        sleep_threshold: float = SLEEP_THRESHOLD,
        retry_delay: float = RETRY_DELAY
    ) -> Any:
        try:
            await asyncio.wait_for(self.is_started.wait(), self.WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            log.warning("Session not started within %ss, proceeding anyway", self.WAIT_TIMEOUT)

        if isinstance(
            query, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)
        ):
            inner_query = query.query
        else:
            inner_query = query

        query_name = ".".join(inner_query.QUALNAME.split(".")[1:])

        for attempt in range(1, retries + 1):
            try:
                return await self.send(query, timeout=timeout)
            except (FloodWaitX, FloodPremiumWaitX) as e:
                amount = e.value

                if amount > sleep_threshold >= 0:
                    raise

                log.warning(
                    '[%s] Waiting for %s seconds before continuing (required by "%s")',
                    self.client.name,
                    amount,
                    query_name,
                )

                await asyncio.sleep(amount)
            except (OSError, InternalServerError, ServiceUnavailable, BadMsgNotification, TimeoutError) as e:
                log.warning(
                    '[%s] Retrying "%s" due to: %s', self.client.name, query_name, str(e) or repr(e)
                )

                await asyncio.sleep(retry_delay)

        raise TimeoutError(f'Failed to invoke "{query_name}" after {retries} retries')

    def __str__(self) -> str:
        return f"Session(dc_id={self.dc_id}, test_mode={self.test_mode}, is_media={self.is_media}, is_cdn={self.is_cdn}, state={self._state.name})"
