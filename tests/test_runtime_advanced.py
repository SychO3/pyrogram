"""Comprehensive tests for the enhanced Runtime class.

Covers RuntimeMetrics, auth key exchange, graceful shutdown phases,
storage backend selection, and connection-lost handling.
"""

import asyncio
from collections import defaultdict
from hashlib import sha1
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
import pytest_asyncio

from pyrogram.bot_handle import BotConfig, BotHandle
from pyrogram.runtime import (
    AUTH_CONCURRENCY_LIMIT,
    SHUTDOWN_RPC_TIMEOUT,
    Runtime,
    RuntimeMetrics,
)
from pyrogram.storage.session_data import SessionData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RUNTIME_KWARGS = dict(
    crypto_workers=1,
    handler_workers=1,
    dispatcher_workers=1,
)

TEST_AUTH_KEY = b"\x01" * 256
TEST_AUTH_KEY_ID = sha1(TEST_AUTH_KEY).digest()[-8:]


def _make_session_data(bot_id: int, auth_key: bytes = None) -> SessionData:
    return SessionData(bot_id=bot_id, auth_key=auth_key)


def _make_mock_storage():
    """Return an AsyncMock that behaves like MultiSQLiteStorage."""
    storage = AsyncMock()
    storage.open = AsyncMock()
    storage.close = AsyncMock()
    storage.read_all_sessions = AsyncMock(return_value=[])
    storage.save_session = AsyncMock()
    return storage


def _make_mock_connection_mgr():
    """Return an AsyncMock that behaves like ConnectionManager."""
    mgr = AsyncMock()
    mgr.start = AsyncMock()
    mgr.stop = AsyncMock()
    mgr.remove_bot = AsyncMock(return_value=[])
    mgr.on_connection_lost = AsyncMock(return_value=0.0)
    mgr.connection_count = MagicMock(return_value=0)
    return mgr


def _make_mock_dispatcher():
    """Return an AsyncMock that behaves like UpdateDispatcher."""
    dispatcher = AsyncMock()
    dispatcher.start = AsyncMock()
    dispatcher.stop = AsyncMock()
    dispatcher.register_bot = MagicMock()
    dispatcher.unregister_bot = MagicMock()
    return dispatcher


async def _make_started_runtime(storage_path: str, **extra_kwargs) -> Runtime:
    """Create a Runtime and start it with mocked subsystems."""
    kwargs = {**RUNTIME_KWARGS, **extra_kwargs}
    rt = Runtime(storage_path=storage_path, **kwargs)

    mock_storage = _make_mock_storage()
    mock_conn_mgr = _make_mock_connection_mgr()
    mock_dispatcher = _make_mock_dispatcher()

    with (
        patch("pyrogram.runtime.MultiSQLiteStorage", return_value=mock_storage),
        patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
        patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
    ):
        await rt.start()

    return rt


# ---------------------------------------------------------------------------
# 1. RuntimeMetrics (expanded dataclass)
# ---------------------------------------------------------------------------


class TestRuntimeMetricsSnapshot:
    """snapshot() returns all expected fields."""

    def test_snapshot_returns_all_fields(self):
        m = RuntimeMetrics()
        snap = m.snapshot()

        expected_keys = {
            "active_connections",
            "active_connections_per_dc",
            "connection_creates_total",
            "connection_closes_total",
            "total_bots",
            "active_bots",
            "bots_by_state",
            "rpc_requests_total",
            "rpc_errors_total",
            "updates_received_total",
            "flood_waits_total",
            "transport_errors_total",
            "reconnects_total",
        }
        assert set(snap.keys()) == expected_keys

    def test_snapshot_initial_values_are_zero(self):
        m = RuntimeMetrics()
        snap = m.snapshot()

        assert snap["active_connections"] == 0
        assert snap["connection_creates_total"] == 0
        assert snap["connection_closes_total"] == 0
        assert snap["total_bots"] == 0
        assert snap["active_bots"] == 0
        assert snap["rpc_requests_total"] == 0
        assert snap["rpc_errors_total"] == 0
        assert snap["updates_received_total"] == 0
        assert snap["flood_waits_total"] == 0
        assert snap["transport_errors_total"] == 0
        assert snap["reconnects_total"] == 0

    def test_snapshot_dict_fields_are_plain_dicts(self):
        """active_connections_per_dc and bots_by_state are regular dicts,
        not defaultdicts, in the snapshot."""
        m = RuntimeMetrics()
        snap = m.snapshot()
        assert type(snap["active_connections_per_dc"]) is dict
        assert type(snap["bots_by_state"]) is dict


class TestRuntimeMetricsConnectionTracking:
    """record_connection_create/close with dc_id tracking."""

    def test_record_connection_create_increments(self):
        m = RuntimeMetrics()
        m.record_connection_create(dc_id=2)

        assert m.active_connections == 1
        assert m.active_connections_per_dc[2] == 1
        assert m.connection_creates_total == 1

    def test_record_connection_create_multiple_dcs(self):
        m = RuntimeMetrics()
        m.record_connection_create(dc_id=1)
        m.record_connection_create(dc_id=1)
        m.record_connection_create(dc_id=4)

        assert m.active_connections == 3
        assert m.active_connections_per_dc[1] == 2
        assert m.active_connections_per_dc[4] == 1
        assert m.connection_creates_total == 3

    def test_record_connection_close_decrements(self):
        m = RuntimeMetrics()
        m.record_connection_create(dc_id=2)
        m.record_connection_create(dc_id=2)
        m.record_connection_close(dc_id=2)

        assert m.active_connections == 1
        assert m.active_connections_per_dc[2] == 1
        assert m.connection_closes_total == 1

    def test_record_connection_close_never_goes_negative(self):
        m = RuntimeMetrics()
        m.record_connection_close(dc_id=3)

        assert m.active_connections == 0
        assert m.active_connections_per_dc.get(3, 0) == 0
        assert m.connection_closes_total == 1

    def test_record_connection_close_per_dc_never_negative(self):
        m = RuntimeMetrics()
        m.record_connection_create(dc_id=5)
        m.record_connection_close(dc_id=5)
        m.record_connection_close(dc_id=5)

        assert m.active_connections_per_dc[5] == 0

    def test_record_connection_close_unknown_dc_is_safe(self):
        """Closing a connection on a dc_id that was never created should not crash."""
        m = RuntimeMetrics()
        m.record_connection_close(dc_id=99)
        assert m.connection_closes_total == 1
        assert m.active_connections == 0

    def test_active_connections_per_dc_reflects_snapshot(self):
        m = RuntimeMetrics()
        m.record_connection_create(dc_id=1)
        m.record_connection_create(dc_id=2)
        m.record_connection_create(dc_id=2)

        snap = m.snapshot()
        assert snap["active_connections_per_dc"] == {1: 1, 2: 2}
        assert snap["active_connections"] == 3


class TestRuntimeMetricsRPC:
    """record_rpc_request and record_rpc_error."""

    def test_record_rpc_request_increments(self):
        m = RuntimeMetrics()
        m.record_rpc_request()
        m.record_rpc_request()

        assert m.rpc_requests_total == 2

    def test_record_rpc_error_increments(self):
        m = RuntimeMetrics()
        m.record_rpc_error()
        m.record_rpc_error()
        m.record_rpc_error()

        assert m.rpc_errors_total == 3


class TestRuntimeMetricsUpdates:
    """record_update counting."""

    def test_record_update_increments(self):
        m = RuntimeMetrics()
        for _ in range(5):
            m.record_update()
        assert m.updates_received_total == 5


class TestRuntimeMetricsErrors:
    """record_flood_wait, record_transport_error, record_reconnect."""

    def test_record_flood_wait(self):
        m = RuntimeMetrics()
        m.record_flood_wait()
        m.record_flood_wait()
        assert m.flood_waits_total == 2

    def test_record_transport_error(self):
        m = RuntimeMetrics()
        m.record_transport_error()
        assert m.transport_errors_total == 1

    def test_record_reconnect(self):
        m = RuntimeMetrics()
        m.record_reconnect()
        m.record_reconnect()
        m.record_reconnect()
        assert m.reconnects_total == 3


class TestRuntimeMetricsCallback:
    """on_metrics callback is called on notify events (connection create/close)."""

    def test_on_metrics_called_on_connection_create(self):
        callback = MagicMock()
        m = RuntimeMetrics(_on_metrics=callback)

        m.record_connection_create(dc_id=1)

        callback.assert_called_once()
        snap = callback.call_args[0][0]
        assert snap["active_connections"] == 1
        assert snap["connection_creates_total"] == 1

    def test_on_metrics_called_on_connection_close(self):
        callback = MagicMock()
        m = RuntimeMetrics(_on_metrics=callback)

        m.record_connection_create(dc_id=2)
        callback.reset_mock()

        m.record_connection_close(dc_id=2)

        callback.assert_called_once()
        snap = callback.call_args[0][0]
        assert snap["active_connections"] == 0
        assert snap["connection_closes_total"] == 1

    def test_on_metrics_not_called_for_rpc_methods(self):
        """record_rpc_request, record_rpc_error, record_update, etc.
        do NOT call _notify, so the callback should not fire."""
        callback = MagicMock()
        m = RuntimeMetrics(_on_metrics=callback)

        m.record_rpc_request()
        m.record_rpc_error()
        m.record_update()
        m.record_flood_wait()
        m.record_transport_error()
        m.record_reconnect()

        callback.assert_not_called()

    def test_on_metrics_callback_exception_is_suppressed(self):
        """If the callback raises, it should not propagate."""
        callback = MagicMock(side_effect=ValueError("boom"))
        m = RuntimeMetrics(_on_metrics=callback)

        # Should not raise
        m.record_connection_create(dc_id=1)
        assert m.active_connections == 1

    def test_on_metrics_none_is_noop(self):
        """When _on_metrics is None, _notify is a no-op."""
        m = RuntimeMetrics(_on_metrics=None)
        m.record_connection_create(dc_id=1)  # should not raise
        assert m.connection_creates_total == 1

    def test_on_metrics_receives_fresh_snapshot_each_time(self):
        snapshots = []
        callback = MagicMock(side_effect=lambda snap: snapshots.append(snap.copy()))
        m = RuntimeMetrics(_on_metrics=callback)

        m.record_connection_create(dc_id=1)
        m.record_connection_create(dc_id=1)

        assert len(snapshots) == 2
        assert snapshots[0]["active_connections"] == 1
        assert snapshots[1]["active_connections"] == 2


# ---------------------------------------------------------------------------
# 2. Auth key exchange (create_auth_key method)
# ---------------------------------------------------------------------------


class TestCreateAuthKey:
    """Auth key exchange with semaphore, BotHandle update, and storage persist."""

    @pytest.mark.asyncio
    async def test_create_auth_key_updates_bot_and_storage(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            # Add a bot
            data = _make_session_data(100)
            bot = await rt.add_bot(data, BotConfig(api_id=999))

            fake_auth_key = b"\xAB" * 256

            mock_auth_instance = AsyncMock()
            mock_auth_instance.create = AsyncMock(return_value=fake_auth_key)

            with patch("pyrogram.session.auth.Auth", return_value=mock_auth_instance) as MockAuth:
                result = await rt.create_auth_key(
                    bot=bot,
                    dc_id=2,
                    server_address="149.154.167.51",
                    port=443,
                    test_mode=False,
                )

            # Verify the key was returned
            assert result == fake_auth_key

            # Verify bot's auth_key was updated
            assert bot.auth_key == fake_auth_key

            # Verify auth_key_id was computed correctly
            expected_id = sha1(fake_auth_key).digest()[-8:]
            assert bot.auth_key_id == expected_id

            # Verify bot is in the auth_key_index
            assert rt._auth_key_index[expected_id] is bot

            # Verify storage was updated (BotStorageProxy delegates to
            # rt.storage.set_session_field)
            rt.storage.set_session_field.assert_awaited_with(
                100, "auth_key", fake_auth_key
            )
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_create_auth_key_semaphore_limits_concurrency(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            data = _make_session_data(200)
            bot = await rt.add_bot(data, BotConfig(api_id=999))

            # Track concurrency
            max_concurrent = 0
            current_concurrent = 0
            lock = asyncio.Lock()

            async def slow_create():
                nonlocal max_concurrent, current_concurrent
                async with lock:
                    current_concurrent += 1
                    max_concurrent = max(max_concurrent, current_concurrent)
                await asyncio.sleep(0.01)
                async with lock:
                    current_concurrent -= 1
                return b"\xCC" * 256

            mock_auth = AsyncMock()
            mock_auth.create = slow_create

            with patch("pyrogram.session.auth.Auth", return_value=mock_auth):
                # Launch more tasks than the semaphore limit
                tasks = [
                    rt.create_auth_key(bot, dc_id=2, server_address="x", port=443, test_mode=False)
                    for _ in range(AUTH_CONCURRENCY_LIMIT + 10)
                ]
                await asyncio.gather(*tasks)

            # Concurrency should never exceed the semaphore limit
            assert max_concurrent <= AUTH_CONCURRENCY_LIMIT
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_create_auth_key_passes_correct_params_to_auth(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            data = _make_session_data(300)
            bot = await rt.add_bot(data, BotConfig(api_id=777))

            mock_auth_instance = AsyncMock()
            mock_auth_instance.create = AsyncMock(return_value=b"\xDD" * 256)

            with patch("pyrogram.session.auth.Auth", return_value=mock_auth_instance) as MockAuth:
                await rt.create_auth_key(
                    bot=bot,
                    dc_id=4,
                    server_address="10.0.0.1",
                    port=8443,
                    test_mode=True,
                )

            MockAuth.assert_called_once_with(
                client=bot,
                dc_id=4,
                server_address="10.0.0.1",
                port=8443,
                test_mode=True,
            )
            mock_auth_instance.create.assert_awaited_once()
        finally:
            await rt.stop()


# ---------------------------------------------------------------------------
# 3. Graceful shutdown (stop method phases)
# ---------------------------------------------------------------------------


class TestGracefulShutdown:
    """Test the multi-phase shutdown sequence."""

    @pytest.mark.asyncio
    async def test_phase1_pending_acks_flushed(self, tmp_path):
        """Phase 1: pending ACKs are sent before stopping."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(10, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        # Mock session with pending_acks
        mock_session = AsyncMock()
        mock_session.pending_acks = {111, 222, 333}
        mock_session.send = AsyncMock()
        mock_session.results = {}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        await rt.stop()

        # Verify ACKs were flushed
        mock_session.send.assert_awaited_once()
        sent_call = mock_session.send.call_args
        # The raw.types.MsgsAck msg_ids should contain our pending ACK IDs
        ack_msg = sent_call[0][0]
        assert set(ack_msg.msg_ids) == {111, 222, 333}
        assert sent_call[1]["wait_response"] is False

    @pytest.mark.asyncio
    async def test_phase2_inflight_rpc_wait(self, tmp_path):
        """Phase 2: waits for in-flight RPCs with timeout."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(20, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        # Mock session with an in-flight RPC that completes quickly
        event = asyncio.Event()
        result_mock = MagicMock()
        result_mock.value = None
        result_mock.event = event

        mock_session = AsyncMock()
        mock_session.pending_acks = set()
        mock_session.results = {"msg_1": result_mock}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        # Resolve the RPC shortly after stop begins
        async def resolve_later():
            await asyncio.sleep(0.05)
            result_mock.value = "done"
            event.set()

        asyncio.get_event_loop().create_task(resolve_later())

        await rt.stop()

        # Should have waited and RPC resolved
        assert event.is_set()

    @pytest.mark.asyncio
    async def test_phase2_inflight_rpc_timeout(self, tmp_path):
        """Phase 2: if RPCs do not complete, stop proceeds after timeout."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(30, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        # RPC that never completes
        event = asyncio.Event()
        result_mock = MagicMock()
        result_mock.value = None
        result_mock.event = event

        mock_session = AsyncMock()
        mock_session.pending_acks = set()
        mock_session.results = {"stuck_rpc": result_mock}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        # Patch SHUTDOWN_RPC_TIMEOUT to something tiny
        with patch("pyrogram.runtime.SHUTDOWN_RPC_TIMEOUT", 0.05):
            await rt.stop()

        # Stop should have completed even though the RPC never resolved
        assert rt._started is False

    @pytest.mark.asyncio
    async def test_phase3_all_sessions_stopped(self, tmp_path):
        """Phase 3: main session + aux sessions + media sessions all stopped."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(40, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        main_session = AsyncMock()
        main_session.pending_acks = set()
        main_session.results = {}
        main_session.stop = AsyncMock()

        aux_session_2 = AsyncMock()
        aux_session_2.stop = AsyncMock()
        aux_session_3 = AsyncMock()
        aux_session_3.stop = AsyncMock()

        media_session_1 = AsyncMock()
        media_session_1.stop = AsyncMock()

        bot.session = main_session
        bot.sessions = {2: aux_session_2, 3: aux_session_3}
        bot.media_sessions = {1: media_session_1}

        await rt.stop()

        main_session.stop.assert_awaited_once()
        aux_session_2.stop.assert_awaited_once()
        aux_session_3.stop.assert_awaited_once()
        media_session_1.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_phase4_through_7_shutdown_order(self, tmp_path):
        """Phases 4-7: connection_mgr, dispatcher, storage, executors shut down."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        # Capture stop calls and their order
        call_order = []

        original_conn_mgr_stop = rt.connection_mgr.stop

        async def conn_mgr_stop():
            call_order.append("connection_mgr")
            return await original_conn_mgr_stop()

        original_dispatcher_stop = rt.update_dispatcher.stop

        async def dispatcher_stop():
            call_order.append("dispatcher")
            return await original_dispatcher_stop()

        original_storage_close = rt.storage.close

        async def storage_close():
            call_order.append("storage")
            return await original_storage_close()

        rt.connection_mgr.stop = conn_mgr_stop
        rt.update_dispatcher.stop = dispatcher_stop
        rt.storage.close = storage_close

        # We cannot easily intercept executor.shutdown, but we can verify
        # the executors exist before stop and the runtime state after.
        assert rt.crypto_executor is not None
        assert rt.handler_executor is not None

        await rt.stop()

        assert call_order == ["connection_mgr", "dispatcher", "storage"]
        assert rt._started is False
        assert rt._stopping is False
        assert len(rt.bots) == 0

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self, tmp_path):
        """Calling stop() on an already-stopped runtime is a no-op."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        await rt.stop()
        # Second stop should be a no-op
        await rt.stop()

        assert rt._started is False

    @pytest.mark.asyncio
    async def test_stop_not_started_is_noop(self, tmp_path):
        """Calling stop() on a runtime that was never started is a no-op."""
        rt = Runtime(storage_path=str(tmp_path / "test.db"), **RUNTIME_KWARGS)
        await rt.stop()  # should not raise
        assert rt._started is False

    @pytest.mark.asyncio
    async def test_stop_clears_auth_key_index(self, tmp_path):
        """After stop, _auth_key_index is empty."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(50, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        # Mock session so phase 3 doesn't error
        mock_session = AsyncMock()
        mock_session.pending_acks = set()
        mock_session.results = {}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        assert len(rt._auth_key_index) > 0

        await rt.stop()

        assert len(rt._auth_key_index) == 0

    @pytest.mark.asyncio
    async def test_phase1_no_pending_acks_is_fine(self, tmp_path):
        """Phase 1 with no pending ACKs should not send anything."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(60, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        mock_session = AsyncMock()
        mock_session.pending_acks = set()  # empty
        mock_session.results = {}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        await rt.stop()

        mock_session.send.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_phase1_ack_send_failure_is_suppressed(self, tmp_path):
        """If sending ACKs fails, shutdown continues."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(70, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        mock_session = AsyncMock()
        mock_session.pending_acks = {999}
        mock_session.send = AsyncMock(side_effect=ConnectionError("gone"))
        mock_session.results = {}
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        # Should not raise
        await rt.stop()
        assert rt._started is False


# ---------------------------------------------------------------------------
# 4. Storage backend selection
# ---------------------------------------------------------------------------


class TestStorageBackendSelection:
    """start() selects the correct storage backend."""

    @pytest.mark.asyncio
    async def test_default_sqlite_backend(self, tmp_path):
        """Default storage_backend='sqlite' uses MultiSQLiteStorage."""
        rt = Runtime(storage_path=str(tmp_path / "test.db"), **RUNTIME_KWARGS)

        mock_storage = _make_mock_storage()
        mock_conn_mgr = _make_mock_connection_mgr()
        mock_dispatcher = _make_mock_dispatcher()

        with (
            patch("pyrogram.runtime.MultiSQLiteStorage", return_value=mock_storage) as MockSQLite,
            patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
            patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
        ):
            await rt.start()

        MockSQLite.assert_called_once_with(str(tmp_path / "test.db"))
        assert rt.storage is mock_storage
        mock_storage.open.assert_awaited_once()

        await rt.stop()

    @pytest.mark.asyncio
    async def test_redis_backend_selection(self, tmp_path):
        """storage_backend='redis' uses RedisStorage."""
        redis_uri = "redis://myhost:6380/2"
        rt = Runtime(
            storage_path=str(tmp_path / "test.db"),
            storage_backend="redis",
            redis_uri=redis_uri,
            **RUNTIME_KWARGS,
        )

        mock_redis_storage = _make_mock_storage()
        mock_conn_mgr = _make_mock_connection_mgr()
        mock_dispatcher = _make_mock_dispatcher()

        with (
            patch("pyrogram.storage.redis_storage.RedisStorage", return_value=mock_redis_storage) as MockRedis,
            patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
            patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
        ):
            await rt.start()

        MockRedis.assert_called_once_with(redis_uri)
        assert rt.storage is mock_redis_storage
        mock_redis_storage.open.assert_awaited_once()

        await rt.stop()


# ---------------------------------------------------------------------------
# 5. on_bot_connection_lost
# ---------------------------------------------------------------------------


class TestOnBotConnectionLost:
    """on_bot_connection_lost records reconnect metric and delegates."""

    @pytest.mark.asyncio
    async def test_records_reconnect_metric(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            data = _make_session_data(500, auth_key=TEST_AUTH_KEY)
            bot = await rt.add_bot(data, BotConfig(api_id=1))

            assert rt.metrics.reconnects_total == 0

            await rt.on_bot_connection_lost(bot_id=500, dc_id=2)

            assert rt.metrics.reconnects_total == 1
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_delegates_to_connection_mgr(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            data = _make_session_data(600, auth_key=TEST_AUTH_KEY)
            await rt.add_bot(data, BotConfig(api_id=1))

            await rt.on_bot_connection_lost(bot_id=600, dc_id=4)

            rt.connection_mgr.on_connection_lost.assert_awaited_once_with(4, 600)
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_unknown_bot_id_is_noop(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            initial_reconnects = rt.metrics.reconnects_total

            await rt.on_bot_connection_lost(bot_id=9999, dc_id=1)

            # Should not have recorded a reconnect for unknown bot
            assert rt.metrics.reconnects_total == initial_reconnects
            rt.connection_mgr.on_connection_lost.assert_not_awaited()
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_multiple_connection_lost_events(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            data = _make_session_data(700, auth_key=TEST_AUTH_KEY)
            await rt.add_bot(data, BotConfig(api_id=1))

            for _ in range(5):
                await rt.on_bot_connection_lost(bot_id=700, dc_id=2)

            assert rt.metrics.reconnects_total == 5
            assert rt.connection_mgr.on_connection_lost.await_count == 5
        finally:
            await rt.stop()


# ---------------------------------------------------------------------------
# 6. Runtime.__init__ parameter wiring
# ---------------------------------------------------------------------------


class TestRuntimeInit:
    """Verify constructor wires parameters correctly."""

    def test_default_values(self):
        rt = Runtime()
        assert rt._storage_backend == "sqlite"
        assert rt._storage_path == "bots.db"
        assert rt._max_connections_per_dc == 100
        assert rt._idle_timeout == 60.0
        assert rt._handler_workers == 32
        assert rt._dispatcher_workers == 32
        assert rt.proxy is None
        assert rt._started is False
        assert rt._stopping is False
        assert rt.bots == {}
        assert rt._auth_key_index == {}

    def test_custom_values(self):
        callback = MagicMock()
        rt = Runtime(
            crypto_workers=4,
            storage_path="custom.db",
            storage_backend="redis",
            redis_uri="redis://custom:1234/5",
            max_connections_per_dc=50,
            idle_timeout=120.0,
            handler_workers=16,
            dispatcher_workers=8,
            proxy={"scheme": "socks5"},
            on_metrics=callback,
        )

        assert rt._crypto_workers == 4
        assert rt._storage_path == "custom.db"
        assert rt._storage_backend == "redis"
        assert rt._redis_uri == "redis://custom:1234/5"
        assert rt._max_connections_per_dc == 50
        assert rt._idle_timeout == 120.0
        assert rt._handler_workers == 16
        assert rt._dispatcher_workers == 8
        assert rt.proxy == {"scheme": "socks5"}
        assert rt.metrics._on_metrics is callback

    def test_auth_semaphore_limit(self):
        rt = Runtime()
        assert rt._auth_semaphore._value == AUTH_CONCURRENCY_LIMIT


# ---------------------------------------------------------------------------
# 7. Runtime.start() validation and double-start guard
# ---------------------------------------------------------------------------


class TestRuntimeStart:
    """start() initialization and guards."""

    @pytest.mark.asyncio
    async def test_double_start_raises(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            with pytest.raises(RuntimeError, match="already started"):
                await rt.start()
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_start_creates_executors(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            assert rt.crypto_executor is not None
            assert rt.handler_executor is not None
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_start_loads_existing_sessions(self, tmp_path):
        """start() loads sessions from storage and registers them."""
        rt = Runtime(storage_path=str(tmp_path / "test.db"), **RUNTIME_KWARGS)

        existing_session = SessionData(bot_id=42, auth_key=TEST_AUTH_KEY, api_id=111)
        mock_storage = _make_mock_storage()
        mock_storage.read_all_sessions = AsyncMock(return_value=[existing_session])

        mock_conn_mgr = _make_mock_connection_mgr()
        mock_dispatcher = _make_mock_dispatcher()

        with (
            patch("pyrogram.runtime.MultiSQLiteStorage", return_value=mock_storage),
            patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
            patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
        ):
            await rt.start()

        try:
            assert 42 in rt.bots
            assert rt.bots[42].bot_id == 42
            mock_dispatcher.register_bot.assert_called_with(42)
        finally:
            await rt.stop()


# ---------------------------------------------------------------------------
# 8. add_bot guards
# ---------------------------------------------------------------------------


class TestAddBotGuards:
    """add_bot raises on bad state."""

    @pytest.mark.asyncio
    async def test_add_bot_when_stopping_raises(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        rt._stopping = True
        try:
            with pytest.raises(RuntimeError, match="stopping"):
                await rt.add_bot(_make_session_data(1), BotConfig(api_id=1))
        finally:
            rt._stopping = False
            await rt.stop()


# ---------------------------------------------------------------------------
# 9. Async context manager
# ---------------------------------------------------------------------------


class TestAsyncContextManager:
    """__aenter__ / __aexit__ work correctly."""

    @pytest.mark.asyncio
    async def test_context_manager_starts_and_stops(self, tmp_path):
        rt = Runtime(storage_path=str(tmp_path / "test.db"), **RUNTIME_KWARGS)

        mock_storage = _make_mock_storage()
        mock_conn_mgr = _make_mock_connection_mgr()
        mock_dispatcher = _make_mock_dispatcher()

        with (
            patch("pyrogram.runtime.MultiSQLiteStorage", return_value=mock_storage),
            patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
            patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
        ):
            async with rt as runtime:
                assert runtime._started is True
                assert runtime is rt

        assert rt._started is False


# ---------------------------------------------------------------------------
# 10. Encrypt / decrypt delegate to executor
# ---------------------------------------------------------------------------


class TestCryptoOperations:
    """encrypt() records RPC metric and delegates to executor."""

    @pytest.mark.asyncio
    async def test_encrypt_records_rpc_request(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            assert rt.metrics.rpc_requests_total == 0

            with patch("pyrogram.crypto.mtproto.pack", return_value=b"encrypted"):
                result = await rt.encrypt(
                    auth_key=TEST_AUTH_KEY,
                    auth_key_id=TEST_AUTH_KEY_ID,
                    message=MagicMock(),
                    salt=0,
                    session_id=b"\x00" * 8,
                )

            assert result == b"encrypted"
            assert rt.metrics.rpc_requests_total == 1
        finally:
            await rt.stop()

    @pytest.mark.asyncio
    async def test_decrypt_delegates_to_executor(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            with patch("pyrogram.crypto.mtproto.unpack", return_value="decrypted"):
                result = await rt.decrypt(
                    auth_key=TEST_AUTH_KEY,
                    auth_key_id=TEST_AUTH_KEY_ID,
                    packet=b"\x00" * 32,
                    session_id=b"\x00" * 8,
                )

            assert result == "decrypted"
        finally:
            await rt.stop()


# ---------------------------------------------------------------------------
# 11. repr
# ---------------------------------------------------------------------------


class TestRepr:
    """__repr__ returns a useful string."""

    def test_repr_before_start(self):
        rt = Runtime()
        result = repr(rt)
        assert "Runtime" in result
        assert "bots=0" in result
        assert "connections=0" in result

    @pytest.mark.asyncio
    async def test_repr_after_start(self, tmp_path):
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        try:
            result = repr(rt)
            assert "Runtime" in result
            assert "bots=0" in result
        finally:
            await rt.stop()


# ---------------------------------------------------------------------------
# 12. Combined metrics + shutdown integration
# ---------------------------------------------------------------------------


class TestMetricsAndShutdownIntegration:
    """Verify metrics reflect state after full lifecycle."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_metrics(self, tmp_path):
        callback_snapshots = []
        on_metrics = MagicMock(side_effect=lambda s: callback_snapshots.append(s.copy()))

        rt = Runtime(
            storage_path=str(tmp_path / "test.db"),
            on_metrics=on_metrics,
            **RUNTIME_KWARGS,
        )

        mock_storage = _make_mock_storage()
        mock_conn_mgr = _make_mock_connection_mgr()
        mock_dispatcher = _make_mock_dispatcher()

        with (
            patch("pyrogram.runtime.MultiSQLiteStorage", return_value=mock_storage),
            patch("pyrogram.runtime.ConnectionManager", return_value=mock_conn_mgr),
            patch("pyrogram.runtime.UpdateDispatcher", return_value=mock_dispatcher),
        ):
            await rt.start()

        # Simulate connection lifecycle via metrics
        rt.metrics.record_connection_create(dc_id=1)
        rt.metrics.record_connection_create(dc_id=2)
        rt.metrics.record_rpc_request()
        rt.metrics.record_rpc_request()
        rt.metrics.record_rpc_error()
        rt.metrics.record_update()
        rt.metrics.record_flood_wait()
        rt.metrics.record_transport_error()
        rt.metrics.record_reconnect()
        rt.metrics.record_connection_close(dc_id=1)

        snap = rt.metrics.snapshot()
        assert snap["active_connections"] == 1
        assert snap["connection_creates_total"] == 2
        assert snap["connection_closes_total"] == 1
        assert snap["rpc_requests_total"] == 2
        assert snap["rpc_errors_total"] == 1
        assert snap["updates_received_total"] == 1
        assert snap["flood_waits_total"] == 1
        assert snap["transport_errors_total"] == 1
        assert snap["reconnects_total"] == 1

        # on_metrics was called for connection create (x2) and close (x1)
        assert len(callback_snapshots) == 3

        await rt.stop()


# ---------------------------------------------------------------------------
# 13. Edge case: bot without session during shutdown
# ---------------------------------------------------------------------------


class TestShutdownEdgeCases:
    """Edge cases in the shutdown sequence."""

    @pytest.mark.asyncio
    async def test_bot_with_no_session_during_stop(self, tmp_path):
        """Bots added but never connected (session=None) should not crash stop."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(800, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))
        assert bot.session is None

        # Should complete without error
        await rt.stop()
        assert rt._started is False

    @pytest.mark.asyncio
    async def test_session_stop_failure_during_shutdown(self, tmp_path):
        """If a session.stop() raises during phase 3, shutdown continues."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(810, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        failing_session = AsyncMock()
        failing_session.pending_acks = set()
        failing_session.results = {}
        failing_session.stop = AsyncMock(side_effect=OSError("socket error"))
        bot.session = failing_session

        # Should not raise
        await rt.stop()
        assert rt._started is False

    @pytest.mark.asyncio
    async def test_multiple_bots_all_sessions_stopped(self, tmp_path):
        """All bots' sessions are stopped during shutdown, not just the first."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        sessions = []
        for i in range(5):
            data = _make_session_data(900 + i, auth_key=TEST_AUTH_KEY)
            bot = await rt.add_bot(data, BotConfig(api_id=1))

            mock_s = AsyncMock()
            mock_s.pending_acks = set()
            mock_s.results = {}
            mock_s.stop = AsyncMock()
            bot.session = mock_s
            sessions.append(mock_s)

        await rt.stop()

        for s in sessions:
            s.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_session_without_pending_acks_attr(self, tmp_path):
        """If session does not have pending_acks, phase 1 is skipped for it."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(820, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        mock_session = AsyncMock(spec=[])
        mock_session.stop = AsyncMock()
        # No pending_acks or results attributes
        bot.session = mock_session

        # Should not raise
        await rt.stop()
        assert rt._started is False

    @pytest.mark.asyncio
    async def test_session_without_results_attr(self, tmp_path):
        """If session has pending_acks but no results, phase 2 is skipped for it."""
        rt = await _make_started_runtime(str(tmp_path / "test.db"))

        data = _make_session_data(830, auth_key=TEST_AUTH_KEY)
        bot = await rt.add_bot(data, BotConfig(api_id=1))

        mock_session = MagicMock()
        mock_session.pending_acks = set()
        # Ensure hasattr(session, 'results') is False
        del mock_session.results
        mock_session.stop = AsyncMock()
        bot.session = mock_session

        # Should not raise
        await rt.stop()
        assert rt._started is False
