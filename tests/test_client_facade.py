"""Tests for the Client facade pattern (attach_runtime / detach_runtime)
and Session._notify_connection_lost behaviour.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyrogram.client import Client
from pyrogram.session.session import Session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bare_client() -> Client:
    """Create a Client without running __init__ (avoids heavy side-effects)."""
    client = object.__new__(Client)
    # Set the minimal attributes that the facade methods touch
    client._runtime = None
    client._bot_handle = None
    return client


def _make_runtime() -> SimpleNamespace:
    """Lightweight stand-in for pyrogram.Runtime."""
    return SimpleNamespace(
        crypto_executor=MagicMock(name="crypto_executor"),
    )


def _make_bot_handle() -> MagicMock:
    """Lightweight stand-in for pyrogram.bot_handle.BotHandle."""
    handle = MagicMock(name="BotHandle")
    handle.handle_updates = AsyncMock()
    handle.on_connection_lost = AsyncMock()
    return handle


# =========================================================================
# 1. attach_runtime / detach_runtime
# =========================================================================


class TestAttachDetachRuntime:
    """Verify that Client.attach_runtime and Client.detach_runtime correctly
    wire up and tear down the runtime-related attributes."""

    def test_attach_runtime_sets_attributes(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)

        assert client._runtime is runtime
        assert client._bot_handle is bot_handle

    def test_detach_runtime_clears_attributes(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        client.detach_runtime()

        assert client._runtime is None
        assert client._bot_handle is None

    def test_attach_then_detach_then_reattach(self):
        """Ensure the lifecycle can be repeated without leftover state."""
        client = _make_bare_client()
        rt1 = _make_runtime()
        bh1 = _make_bot_handle()
        rt2 = _make_runtime()
        bh2 = _make_bot_handle()

        client.attach_runtime(rt1, bh1)
        assert client._runtime is rt1
        assert client._bot_handle is bh1

        client.detach_runtime()
        assert client._runtime is None

        client.attach_runtime(rt2, bh2)
        assert client._runtime is rt2
        assert client._bot_handle is bh2


class TestRuntimeProperty:
    """Client.runtime property returns _runtime."""

    def test_runtime_initially_none(self):
        client = _make_bare_client()
        assert client.runtime is None

    def test_runtime_returns_attached_runtime(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        assert client.runtime is runtime

    def test_runtime_none_after_detach(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        client.detach_runtime()
        assert client.runtime is None


class TestBotHandleProperty:
    """Client.bot_handle property returns _bot_handle."""

    def test_bot_handle_initially_none(self):
        client = _make_bare_client()
        assert client.bot_handle is None

    def test_bot_handle_returns_attached_handle(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        assert client.bot_handle is bot_handle

    def test_bot_handle_none_after_detach(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        client.detach_runtime()
        assert client.bot_handle is None


# =========================================================================
# 2. handle_updates delegation
# =========================================================================


class TestHandleUpdatesDelegation:
    """When bot_handle is attached, Client.handle_updates must delegate
    to bot_handle.handle_updates and return immediately."""

    @pytest.mark.asyncio
    async def test_delegates_when_bot_handle_attached(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)

        fake_updates = MagicMock(name="raw_updates")
        await client.handle_updates(fake_updates)

        bot_handle.handle_updates.assert_awaited_once_with(fake_updates)

    @pytest.mark.asyncio
    async def test_does_not_touch_dispatcher_when_attached(self):
        """Verify that the original dispatcher path is not reached."""
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()
        client.attach_runtime(runtime, bot_handle)

        # If the code tried to access self.dispatcher it would AttributeError
        # because _make_bare_client() doesn't set one.  The test passes if
        # no error is raised -- proof that delegation short-circuits.
        await client.handle_updates(MagicMock())

    @pytest.mark.asyncio
    async def test_delegates_multiple_times(self):
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()
        client.attach_runtime(runtime, bot_handle)

        updates_a = MagicMock(name="updates_a")
        updates_b = MagicMock(name="updates_b")

        await client.handle_updates(updates_a)
        await client.handle_updates(updates_b)

        assert bot_handle.handle_updates.await_count == 2
        bot_handle.handle_updates.assert_any_await(updates_a)
        bot_handle.handle_updates.assert_any_await(updates_b)

    @pytest.mark.asyncio
    async def test_no_delegation_after_detach(self):
        """After detach, handle_updates should use the original code path
        and not call bot_handle.handle_updates."""
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()

        client.attach_runtime(runtime, bot_handle)
        client.detach_runtime()

        # The original path sets self.last_update_time and then does
        # isinstance checks.  A MagicMock won't match any raw.types, so the
        # function returns without doing anything meaningful.  We verify
        # that bot_handle.handle_updates is NOT called.
        await client.handle_updates(MagicMock())
        bot_handle.handle_updates.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_delegation_when_never_attached(self):
        """A fresh client with _bot_handle=None should not delegate."""
        client = _make_bare_client()
        bot_handle = _make_bot_handle()

        # handle_updates with unknown update type just falls through
        await client.handle_updates(MagicMock())

        # bot_handle was never attached, so it should never be called
        bot_handle.handle_updates.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delegation_returns_early(self):
        """When delegating, handle_updates should call bot_handle.handle_updates
        and return without touching the dispatcher code path."""
        client = _make_bare_client()
        runtime = _make_runtime()
        bot_handle = _make_bot_handle()
        client.attach_runtime(runtime, bot_handle)

        await client.handle_updates(MagicMock())
        # Delegation path should have called bot_handle
        bot_handle.handle_updates.assert_awaited_once()


# =========================================================================
# 3. Session._notify_connection_lost
# =========================================================================


class TestNotifyConnectionLost:
    """Session._notify_connection_lost should call
    client.on_connection_lost only when the client is a BotHandle."""

    def _make_session(self, client_obj) -> Session:
        """Create a Session with a fake client, bypassing heavy init."""
        session = object.__new__(Session)
        session.client = client_obj
        session.dc_id = 2
        session.server_address = "127.0.0.1"
        session.port = 443
        session.is_media = False
        session.is_cdn = False
        return session

    @pytest.mark.asyncio
    async def test_calls_on_connection_lost_for_bot_handle(self):
        """When client is a BotHandle, _notify_connection_lost fires
        on_connection_lost(dc_id) as an async task."""
        from pyrogram.bot_handle import BotConfig, BotHandle

        loop = asyncio.get_running_loop()
        runtime = SimpleNamespace(
            loop=loop,
            proxy=None,
            connection_factory=object(),
            protocol_factory=object(),
            handler_executor=object(),
            storage=MagicMock(),
            crypto_executor=None,
            update_dispatcher=None,
            metrics=MagicMock(),
            connection_mgr=None,
            on_bot_connection_lost=AsyncMock(),
        )

        bot = BotHandle(runtime, bot_id=42, config=BotConfig(api_id=1), auth_key=b"\x00" * 256)
        bot.on_connection_lost = AsyncMock()

        session = self._make_session(bot)

        # _notify_connection_lost calls asyncio.get_event_loop().create_task(...)
        # We need to capture the coroutine and verify it calls on_connection_lost.
        created_tasks = []
        original_create_task = loop.create_task

        def capturing_create_task(coro, **kwargs):
            task = original_create_task(coro, **kwargs)
            created_tasks.append(task)
            return task

        with patch.object(loop, "create_task", side_effect=capturing_create_task):
            session._notify_connection_lost()

        assert len(created_tasks) == 1
        # Let the task complete
        await created_tasks[0]

        bot.on_connection_lost.assert_awaited_once_with(2)

    def test_does_nothing_for_regular_client(self):
        """When client is a regular Client, _notify_connection_lost is a no-op."""
        client = _make_bare_client()
        session = self._make_session(client)

        # Should not raise, should not create any task
        session._notify_connection_lost()

    def test_does_nothing_for_arbitrary_object(self):
        """When client is some other object, _notify_connection_lost is a no-op."""
        session = self._make_session(SimpleNamespace(name="fake"))

        # Should not raise
        session._notify_connection_lost()

    def test_does_nothing_when_client_is_none(self):
        """Edge case: client is None."""
        session = self._make_session(None)

        session._notify_connection_lost()


# =========================================================================
# 4. Integration: Client.__init__ sets facade defaults
# =========================================================================


class TestClientInitFacadeDefaults:
    """Verify that a normally-constructed Client has the expected facade
    attributes from __init__."""

    def test_defaults_no_runtime(self):
        client = Client("test", api_id=123, api_hash="abc", in_memory=True)
        assert client._runtime is None
        assert client._bot_handle is None

    def test_runtime_param_forwarded(self):
        """When runtime is passed to __init__, it is stored."""
        runtime = _make_runtime()
        client = Client("test", api_id=123, api_hash="abc", in_memory=True, runtime=runtime)
        assert client._runtime is runtime
        # bot_handle is not set via __init__ (only via attach_runtime)
        assert client._bot_handle is None

    def test_runtime_none_explicit(self):
        client = Client("test", api_id=123, api_hash="abc", in_memory=True, runtime=None)
        assert client._runtime is None


# =========================================================================
# 5. _schedule_restart calls _notify_connection_lost
# =========================================================================


class TestScheduleRestartNotifies:
    """Session._schedule_restart should call _notify_connection_lost
    before scheduling the restart task."""

    def test_schedule_restart_calls_notify(self):
        """Verify _schedule_restart invokes _notify_connection_lost."""
        client = _make_bare_client()
        client.loop = MagicMock()
        client.loop.create_task = MagicMock(return_value=MagicMock())

        session = object.__new__(Session)
        session.client = client
        session.dc_id = 1
        session.server_address = "127.0.0.1"
        session.port = 443
        session.is_media = False
        session.is_cdn = False

        with patch.object(session, "_notify_connection_lost") as mock_notify:
            session._schedule_restart("test reason")
            mock_notify.assert_called_once()
