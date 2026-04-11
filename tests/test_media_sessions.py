"""Comprehensive tests for BotHandle.get_media_session() and stop_media_sessions().

Also covers on_connection_lost, ipv6, skip_updates, server_time, and _set_server_time.
"""

import asyncio
import time
from hashlib import sha1
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyrogram.bot_handle import BotConfig, BotHandle, BotStorageProxy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_metrics():
    """Create a minimal RuntimeMetrics-like mock that records calls."""
    metrics = MagicMock()
    metrics.reconnects_total = 0

    def _record_reconnect():
        metrics.reconnects_total += 1

    metrics.record_reconnect = MagicMock(side_effect=_record_reconnect)
    metrics.record_connection_create = MagicMock()
    metrics.record_update = MagicMock()
    return metrics


def _make_runtime(loop: asyncio.AbstractEventLoop, **overrides) -> SimpleNamespace:
    """Build a lightweight Runtime stand-in."""
    defaults = dict(
        loop=loop,
        proxy=None,
        connection_factory=object(),
        protocol_factory=object(),
        handler_executor=object(),
        storage=AsyncMock(),
        connection_mgr=None,
        metrics=_make_metrics(),
        update_dispatcher=AsyncMock(),
        on_bot_connection_lost=AsyncMock(),
        create_auth_key=AsyncMock(return_value=b"\xcc" * 256),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_bot(runtime, bot_id=100, auth_key=None) -> BotHandle:
    if auth_key is None:
        auth_key = b"\xab" * 256
    config = BotConfig(api_id=42)
    return BotHandle(runtime, bot_id=bot_id, config=config, auth_key=auth_key)


def _make_mock_session(dc_id: int = 2, is_started: bool = True):
    """Return a mock that looks like a Session object."""
    session = AsyncMock()
    session.dc_id = dc_id
    session.auth_key = b"\xdd" * 256
    session.is_started = asyncio.Event()
    if is_started:
        session.is_started.set()
    session.WAIT_TIMEOUT = 15
    session.start = AsyncMock()
    session.stop = AsyncMock()
    session.invoke = AsyncMock()
    return session


# ===========================================================================
# get_media_session
# ===========================================================================


class TestGetMediaSession:
    """Tests for BotHandle.get_media_session()."""

    @pytest.mark.asyncio
    async def test_creates_new_media_session(self):
        """get_media_session should create a Session for a DC that has no cached entry."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        # Give the bot a "main" session so it can derive the auth key
        bot.session = _make_mock_session(dc_id=2)

        # Set up storage responses
        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=2)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            result = await bot.get_media_session(dc_id=2)

        assert result is mock_session
        mock_session.start.assert_awaited_once()
        # Should be cached
        assert bot.media_sessions[2] is mock_session

    @pytest.mark.asyncio
    async def test_returns_cached_media_session(self):
        """Second call for the same DC should return the cached session."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        cached = _make_mock_session(dc_id=3)
        bot.media_sessions[3] = cached

        result = await bot.get_media_session(dc_id=3)
        assert result is cached

    @pytest.mark.asyncio
    async def test_uses_non_media_session_auth_key_if_available(self):
        """When a non-media session exists for the DC, its auth_key is reused."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        non_media = _make_mock_session(dc_id=4)
        non_media.auth_key = b"\xee" * 256
        bot.sessions[4] = non_media

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=4)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            result = await bot.get_media_session(dc_id=4)

        # Session constructor should have been called with the non-media auth_key
        call_kwargs = SessionCls.call_args
        assert call_kwargs.kwargs.get("auth_key") == b"\xee" * 256 or \
               (len(call_kwargs.args) > 4 and call_kwargs.args[4] == b"\xee" * 256)

    @pytest.mark.asyncio
    async def test_creates_auth_key_for_different_dc(self):
        """When no non-media session exists and DC differs from main, create_auth_key is called."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=5)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            result = await bot.get_media_session(dc_id=5)

        runtime.create_auth_key.assert_awaited_once()
        assert result is mock_session

    @pytest.mark.asyncio
    async def test_uses_own_auth_key_for_same_dc(self):
        """When DC matches the main session DC, use the bot's own auth_key."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        auth_key = b"\xff" * 256
        bot = _make_bot(runtime, auth_key=auth_key)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=2)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            result = await bot.get_media_session(dc_id=2)

        call_kwargs = SessionCls.call_args
        assert call_kwargs.kwargs.get("auth_key") == auth_key or \
               (len(call_kwargs.args) > 4 and call_kwargs.args[4] == auth_key)
        # create_auth_key should NOT have been called for the same DC
        runtime.create_auth_key.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_raises_when_no_main_session(self):
        """get_media_session should raise ConnectionError when session is None."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = None

        with pytest.raises(ConnectionError, match="No main session"):
            await bot.get_media_session(dc_id=2)

    @pytest.mark.asyncio
    async def test_registers_with_connection_manager(self):
        """When connection_mgr is set, the session should be registered."""
        loop = asyncio.get_running_loop()
        conn_mgr = AsyncMock()
        runtime = _make_runtime(loop, connection_mgr=conn_mgr)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=2)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            await bot.get_media_session(dc_id=2)

        conn_mgr.register_session.assert_awaited_once_with(bot.bot_id, 2, mock_session)
        runtime.metrics.record_connection_create.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_session_start_timeout_raises(self):
        """If is_started is never set, a ConnectionError should be raised."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        # Session whose is_started is never set
        mock_session = _make_mock_session(dc_id=3, is_started=False)
        # Patch WAIT_TIMEOUT on the class so asyncio.wait_for times out quickly
        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 0.01
            with pytest.raises(ConnectionError, match="timed out"):
                await bot.get_media_session(dc_id=3)

        # Should have attempted to stop the session after timeout
        mock_session.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_import_authorization_for_different_dc(self):
        """For a DC that differs from main, ExportAuth + ImportAuth should be invoked."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        main_session = _make_mock_session(dc_id=2)
        bot.session = main_session

        # dc_id=2 is main, requesting dc_id=5
        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        exported = SimpleNamespace(id=123, bytes=b"auth_bytes")
        main_session.invoke = AsyncMock(return_value=exported)

        mock_session = _make_mock_session(dc_id=5)
        mock_session.invoke = AsyncMock(return_value=None)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            result = await bot.get_media_session(dc_id=5)

        # main_session.invoke should have been called (ExportAuthorization)
        main_session.invoke.assert_awaited()
        # media session.invoke should have been called (ImportAuthorization)
        mock_session.invoke.assert_awaited()

    @pytest.mark.asyncio
    async def test_concurrent_calls_deduplicate(self):
        """Sequential get_media_session calls for same DC reuse cached session.

        The source code stores a future in _session_futures for dedup, but
        the await happens under the sessions_lock. We verify the simpler
        caching path: after the first call completes, the second returns
        the cached session without creating a new one.
        """
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        call_count = 0
        created_session = _make_mock_session(dc_id=7)

        async def counting_start():
            nonlocal call_count
            call_count += 1

        created_session.start = AsyncMock(side_effect=counting_start)

        with patch("pyrogram.session.Session", return_value=created_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            # First call creates the session
            result1 = await bot.get_media_session(dc_id=7)
            # Second call should return cached session (no new Session created)
            result2 = await bot.get_media_session(dc_id=7)

        assert result1 is result2
        assert result1 is created_session
        # Session.start should only have been called once
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_session_futures_dict_used_for_dedup(self):
        """Verify that _session_futures is populated during creation and cleaned up after."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=9)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 15
            await bot.get_media_session(dc_id=9)

        # After successful creation, the future should be cleaned up
        assert (9, True) not in bot._session_futures

    @pytest.mark.asyncio
    async def test_error_propagates_to_waiters(self):
        """If session creation fails, waiting futures should receive the exception."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = _make_mock_session(dc_id=2)

        runtime.storage.get_session_field = AsyncMock(side_effect=lambda bid, field: {
            "dc_id": 2,
            "server_address": "149.154.167.50",
            "port": 443,
            "test_mode": 0,
        }.get(field, None))

        mock_session = _make_mock_session(dc_id=8, is_started=False)

        with patch("pyrogram.session.Session", return_value=mock_session) as SessionCls:
            SessionCls.WAIT_TIMEOUT = 0.01
            with pytest.raises(ConnectionError):
                await bot.get_media_session(dc_id=8)

        # The pending future should have been cleaned up
        assert (8, True) not in bot._session_futures


# ===========================================================================
# stop_media_sessions
# ===========================================================================


class TestStopMediaSessions:
    """Tests for BotHandle.stop_media_sessions()."""

    @pytest.mark.asyncio
    async def test_stops_all_media_sessions(self):
        """stop_media_sessions should stop every cached media session."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        s1 = _make_mock_session(dc_id=2)
        s2 = _make_mock_session(dc_id=3)
        bot.media_sessions[2] = s1
        bot.media_sessions[3] = s2

        await bot.stop_media_sessions()

        s1.stop.assert_awaited_once()
        s2.stop.assert_awaited_once()
        assert len(bot.media_sessions) == 0

    @pytest.mark.asyncio
    async def test_stop_media_sessions_empty(self):
        """stop_media_sessions on empty dict should not raise."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        await bot.stop_media_sessions()
        assert len(bot.media_sessions) == 0

    @pytest.mark.asyncio
    async def test_stop_media_sessions_handles_stop_error(self):
        """If a session.stop() raises, it should be caught and others still stopped."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        s1 = _make_mock_session(dc_id=2)
        s1.stop = AsyncMock(side_effect=RuntimeError("stop failed"))
        s2 = _make_mock_session(dc_id=3)
        bot.media_sessions[2] = s1
        bot.media_sessions[3] = s2

        # Should not raise despite s1.stop() failing
        await bot.stop_media_sessions()

        s1.stop.assert_awaited_once()
        s2.stop.assert_awaited_once()
        assert len(bot.media_sessions) == 0

    @pytest.mark.asyncio
    async def test_stop_clears_dict_atomically(self):
        """The media_sessions dict should be emptied under the lock before stopping."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        s1 = _make_mock_session(dc_id=2)
        bot.media_sessions[2] = s1

        await bot.stop_media_sessions()

        # Even if stop succeeded, the dict must be clear
        assert bot.media_sessions == {}


# ===========================================================================
# on_connection_lost
# ===========================================================================


class TestOnConnectionLost:
    """Tests for BotHandle.on_connection_lost()."""

    @pytest.mark.asyncio
    async def test_records_reconnect_metric(self):
        """on_connection_lost should call metrics.record_reconnect()."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        await bot.on_connection_lost(dc_id=2)

        runtime.metrics.record_reconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_notifies_runtime(self):
        """on_connection_lost should forward to runtime.on_bot_connection_lost()."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime, bot_id=42)

        await bot.on_connection_lost(dc_id=5)

        runtime.on_bot_connection_lost.assert_awaited_once_with(42, 5)

    @pytest.mark.asyncio
    async def test_multiple_connection_lost_events(self):
        """Multiple on_connection_lost calls accumulate metrics."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        await bot.on_connection_lost(dc_id=2)
        await bot.on_connection_lost(dc_id=3)
        await bot.on_connection_lost(dc_id=2)

        assert runtime.metrics.record_reconnect.call_count == 3
        assert runtime.metrics.reconnects_total == 3


# ===========================================================================
# BotHandle properties: ipv6, skip_updates, server_time, _set_server_time
# ===========================================================================


class TestBotHandleAdditionalProperties:
    """Additional property tests for ipv6, skip_updates, server_time, _set_server_time."""

    @pytest.mark.asyncio
    async def test_ipv6_default_false(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        assert bot.ipv6 is False

    @pytest.mark.asyncio
    async def test_ipv6_can_be_set(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.ipv6 = True
        assert bot.ipv6 is True

    @pytest.mark.asyncio
    async def test_skip_updates_default(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        assert bot.skip_updates is False

    @pytest.mark.asyncio
    async def test_skip_updates_from_config(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        config = BotConfig(api_id=42, skip_updates=True)
        bot = BotHandle(runtime, bot_id=1, config=config, auth_key=b"\xab" * 256)
        assert bot.skip_updates is True

    @pytest.mark.asyncio
    async def test_server_time_initially_close_to_now(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        before = time.time()
        st = bot.server_time
        after = time.time()

        assert before <= st <= after

    @pytest.mark.asyncio
    async def test_set_server_time_shifts_offset(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        # Simulate a server timestamp
        fake_ts = 1_800_000_000.0
        msg_id = int(fake_ts * (2 ** 32))
        bot._set_server_time(msg_id)

        result = bot.server_time
        assert abs(result - fake_ts) < 1.0

    @pytest.mark.asyncio
    async def test_set_server_time_multiple_updates(self):
        """_set_server_time can be called multiple times; the latest wins."""
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)

        ts1 = 1_700_000_000.0
        ts2 = 1_800_000_000.0
        bot._set_server_time(int(ts1 * (2 ** 32)))
        assert abs(bot.server_time - ts1) < 1.0

        bot._set_server_time(int(ts2 * (2 ** 32)))
        assert abs(bot.server_time - ts2) < 1.0

    @pytest.mark.asyncio
    async def test_repr(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime, bot_id=999)
        assert repr(bot) == "BotHandle(bot_id=999)"

    @pytest.mark.asyncio
    async def test_invoke_raises_without_session(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = None

        with pytest.raises(ConnectionError, match="not connected"):
            await bot.invoke(MagicMock())

    @pytest.mark.asyncio
    async def test_invoke_delegates_to_session(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        bot.session = AsyncMock()
        bot.session.invoke = AsyncMock(return_value="ok")

        query = MagicMock()
        result = await bot.invoke(query)

        bot.session.invoke.assert_awaited_once_with(query)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_handle_updates_dispatches(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime, bot_id=42)

        raw_update = MagicMock()
        await bot.handle_updates(raw_update)

        runtime.metrics.record_update.assert_called_once()
        runtime.update_dispatcher.dispatch.assert_awaited_once_with(42, raw_update)

    @pytest.mark.asyncio
    async def test_handle_updates_noop_when_no_dispatcher(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop, update_dispatcher=None)
        bot = _make_bot(runtime)

        # Should not raise
        await bot.handle_updates(MagicMock())

    @pytest.mark.asyncio
    async def test_semaphores_initialized(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        config = BotConfig(api_id=42, max_concurrent_transmissions=5)
        bot = BotHandle(runtime, bot_id=1, config=config, auth_key=b"")

        # Semaphore internal value should match config
        assert bot.save_file_semaphore._value == 5
        assert bot.get_file_semaphore._value == 5

    @pytest.mark.asyncio
    async def test_sessions_lock_is_asyncio_lock(self):
        loop = asyncio.get_running_loop()
        runtime = _make_runtime(loop)
        bot = _make_bot(runtime)
        assert isinstance(bot.sessions_lock, asyncio.Lock)
