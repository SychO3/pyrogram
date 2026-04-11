import asyncio
from collections import OrderedDict
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyrogram.update_dispatcher import UpdateDispatcher, PARSER_MAP
from pyrogram.handlers import MessageHandler, RawUpdateHandler
from pyrogram.handlers.conversation_handler import ConversationHandler
from pyrogram.raw.types import (
    UpdateNewMessage,
    UpdateEditMessage,
    UpdateDeleteMessages,
    UpdateBotCallbackQuery,
    UpdateUserStatus,
    UpdateBotInlineQuery,
    UpdateMessagePoll,
    UpdateStory,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_bot(bot_id=1):
    """Create a minimal bot-like object with the attributes UpdateDispatcher needs."""
    return SimpleNamespace(
        loop=None,  # will be patched per-test when an event loop is running
        executor=None,
        name=f"test_bot_{bot_id}",
    )


def _make_runtime(bots=None):
    """Create a minimal runtime-like object."""
    return SimpleNamespace(bots=bots or {})


@pytest.fixture
def runtime():
    return _make_runtime()


@pytest.fixture
def dispatcher(runtime):
    return UpdateDispatcher(runtime, worker_count=2)


# ---------------------------------------------------------------------------
# 1. PARSER_MAP populated
# ---------------------------------------------------------------------------

class TestParserMap:
    def test_parser_map_populated(self):
        """PARSER_MAP should contain entries for well-known raw update types."""
        expected_types = [
            UpdateNewMessage,
            UpdateEditMessage,
            UpdateDeleteMessages,
            UpdateBotCallbackQuery,
            UpdateUserStatus,
            UpdateBotInlineQuery,
            UpdateMessagePoll,
            UpdateStory,
        ]
        for update_type in expected_types:
            assert update_type in PARSER_MAP, (
                f"{update_type.__name__} missing from PARSER_MAP"
            )
            parser_fn, handler_type = PARSER_MAP[update_type]
            assert callable(parser_fn)
            assert isinstance(handler_type, type)


# ---------------------------------------------------------------------------
# 2. register / unregister bot
# ---------------------------------------------------------------------------

class TestRegisterUnregister:
    def test_register_creates_groups(self, dispatcher):
        bot_id = 42
        dispatcher.register_bot(bot_id)

        assert bot_id in dispatcher._handler_groups
        groups = dispatcher._handler_groups[bot_id]
        assert isinstance(groups, OrderedDict)
        # Group 0 should exist with the ConversationHandler
        assert 0 in groups
        assert any(isinstance(h, ConversationHandler) for h in groups[0])

    def test_register_is_idempotent(self, dispatcher):
        bot_id = 42
        dispatcher.register_bot(bot_id)
        original_groups = dispatcher._handler_groups[bot_id]
        dispatcher.register_bot(bot_id)
        assert dispatcher._handler_groups[bot_id] is original_groups

    def test_unregister_removes_groups(self, dispatcher):
        bot_id = 42
        dispatcher.register_bot(bot_id)
        dispatcher.unregister_bot(bot_id)

        assert bot_id not in dispatcher._handler_groups
        assert bot_id not in dispatcher._conversation_handlers

    def test_unregister_nonexistent_bot_no_error(self, dispatcher):
        dispatcher.unregister_bot(999)  # should not raise


# ---------------------------------------------------------------------------
# 3. add / remove handler
# ---------------------------------------------------------------------------

class TestAddRemoveHandler:
    def test_add_handler_to_existing_group(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=0)

        handlers_in_group = dispatcher._handler_groups[bot_id][0]
        assert handler in handlers_in_group

    def test_add_handler_creates_new_group(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=5)

        assert 5 in dispatcher._handler_groups[bot_id]
        assert handler in dispatcher._handler_groups[bot_id][5]

    def test_add_handler_auto_registers_bot(self, dispatcher):
        """add_handler should implicitly register the bot if not yet registered."""
        bot_id = 77
        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=0)

        assert bot_id in dispatcher._handler_groups
        assert handler in dispatcher._handler_groups[bot_id][0]

    def test_groups_remain_sorted(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)

        h1 = RawUpdateHandler(AsyncMock())
        h2 = RawUpdateHandler(AsyncMock())
        h3 = RawUpdateHandler(AsyncMock())

        dispatcher.add_handler(bot_id, h1, group=10)
        dispatcher.add_handler(bot_id, h2, group=2)
        dispatcher.add_handler(bot_id, h3, group=5)

        group_keys = list(dispatcher._handler_groups[bot_id].keys())
        assert group_keys == sorted(group_keys)

    def test_remove_handler(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=1)
        assert handler in dispatcher._handler_groups[bot_id][1]

        dispatcher.remove_handler(bot_id, handler, group=1)
        # Group 1 should have been removed entirely since it's now empty
        assert 1 not in dispatcher._handler_groups[bot_id]

    def test_remove_handler_keeps_group_if_others_remain(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)

        h1 = RawUpdateHandler(AsyncMock())
        h2 = RawUpdateHandler(AsyncMock())
        dispatcher.add_handler(bot_id, h1, group=3)
        dispatcher.add_handler(bot_id, h2, group=3)

        dispatcher.remove_handler(bot_id, h1, group=3)
        assert 3 in dispatcher._handler_groups[bot_id]
        assert h2 in dispatcher._handler_groups[bot_id][3]
        assert h1 not in dispatcher._handler_groups[bot_id][3]

    def test_remove_nonexistent_handler_no_error(self, dispatcher):
        bot_id = 1
        dispatcher.register_bot(bot_id)
        handler = RawUpdateHandler(AsyncMock())
        dispatcher.remove_handler(bot_id, handler, group=99)  # should not raise

    def test_remove_from_unregistered_bot_no_error(self, dispatcher):
        handler = RawUpdateHandler(AsyncMock())
        dispatcher.remove_handler(999, handler, group=0)  # should not raise


# ---------------------------------------------------------------------------
# 4. dispatch calls handler
# ---------------------------------------------------------------------------

class TestDispatchCallsHandler:
    @pytest.mark.asyncio
    async def test_dispatch_raw_handler_called(self, runtime):
        """A RawUpdateHandler callback should be invoked for any dispatched update."""
        bot_id = 1
        bot = _make_bot(bot_id)
        bot.loop = asyncio.get_running_loop()
        runtime.bots[bot_id] = bot

        dispatcher = UpdateDispatcher(runtime, worker_count=1)
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=1)

        await dispatcher.start()
        try:
            some_update = SimpleNamespace(foo="bar")
            users = {}
            chats = {}
            await dispatcher.dispatch(bot_id, (some_update, users, chats))

            # Give the worker time to process the queued update
            await asyncio.sleep(0.1)

            callback.assert_called_once()
            call_args = callback.call_args[0]
            # callback(client, update, users, chats)
            assert call_args[0] is bot
            assert call_args[1] is some_update
            assert call_args[2] is users
            assert call_args[3] is chats
        finally:
            await dispatcher.stop()

    @pytest.mark.asyncio
    async def test_dispatch_multiple_updates(self, runtime):
        """Multiple dispatched updates should each trigger the handler."""
        bot_id = 1
        bot = _make_bot(bot_id)
        bot.loop = asyncio.get_running_loop()
        runtime.bots[bot_id] = bot

        dispatcher = UpdateDispatcher(runtime, worker_count=1)
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=1)

        await dispatcher.start()
        try:
            for i in range(3):
                update = SimpleNamespace(index=i)
                await dispatcher.dispatch(bot_id, (update, {}, {}))

            await asyncio.sleep(0.2)
            assert callback.call_count == 3
        finally:
            await dispatcher.stop()


# ---------------------------------------------------------------------------
# 5. dispatch unknown bot
# ---------------------------------------------------------------------------

class TestDispatchUnknownBot:
    @pytest.mark.asyncio
    async def test_dispatch_unknown_bot_does_not_crash(self, runtime):
        """Dispatching to a bot_id not in runtime.bots should be silently ignored."""
        dispatcher = UpdateDispatcher(runtime, worker_count=1)
        await dispatcher.start()
        try:
            # bot_id=999 is not registered and not in runtime.bots
            await dispatcher.dispatch(999, (SimpleNamespace(), {}, {}))
            await asyncio.sleep(0.1)
            # No assertion beyond "no exception raised"
        finally:
            await dispatcher.stop()

    @pytest.mark.asyncio
    async def test_dispatch_registered_bot_not_in_runtime(self, runtime):
        """Bot registered in dispatcher but missing from runtime.bots should be ignored."""
        bot_id = 1
        dispatcher = UpdateDispatcher(runtime, worker_count=1)
        dispatcher.register_bot(bot_id)

        callback = AsyncMock()
        handler = RawUpdateHandler(callback)
        dispatcher.add_handler(bot_id, handler, group=1)

        await dispatcher.start()
        try:
            # bot_id=1 has handlers but is NOT in runtime.bots
            await dispatcher.dispatch(bot_id, (SimpleNamespace(), {}, {}))
            await asyncio.sleep(0.1)
            callback.assert_not_called()
        finally:
            await dispatcher.stop()


# ---------------------------------------------------------------------------
# 6. start / stop
# ---------------------------------------------------------------------------

class TestStartStop:
    @pytest.mark.asyncio
    async def test_start_creates_workers(self, dispatcher):
        assert len(dispatcher._worker_tasks) == 0
        await dispatcher.start()
        assert len(dispatcher._worker_tasks) == dispatcher._worker_count
        for task in dispatcher._worker_tasks:
            assert isinstance(task, asyncio.Task)
            assert not task.done()
        await dispatcher.stop()

    @pytest.mark.asyncio
    async def test_stop_clears_workers(self, dispatcher):
        await dispatcher.start()
        assert len(dispatcher._worker_tasks) > 0
        await dispatcher.stop()
        assert len(dispatcher._worker_tasks) == 0

    @pytest.mark.asyncio
    async def test_stop_without_start(self, dispatcher):
        """Calling stop on a never-started dispatcher should not raise."""
        await dispatcher.stop()
        assert len(dispatcher._worker_tasks) == 0
