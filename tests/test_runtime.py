import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from pyrogram.bot_handle import BotConfig, BotHandle
from pyrogram.runtime import Runtime, RuntimeMetrics
from pyrogram.storage.session_data import SessionData


RUNTIME_KWARGS = dict(
    crypto_workers=1,
    handler_workers=1,
    dispatcher_workers=1,
)

TEST_AUTH_KEY = b"\x01" * 256


def _make_session_data(bot_id: int, auth_key: bytes = None) -> SessionData:
    return SessionData(bot_id=bot_id, auth_key=auth_key)


@pytest.fixture
def storage_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest_asyncio.fixture
async def runtime(storage_path):
    """Provide a started Runtime and stop it after the test."""
    rt = Runtime(storage_path=storage_path, **RUNTIME_KWARGS)
    await rt.start()
    yield rt
    await rt.stop()


# ---- Tests ----


@pytest.mark.asyncio
async def test_start_stop(storage_path):
    rt = Runtime(storage_path=storage_path, **RUNTIME_KWARGS)

    assert rt._started is False
    assert rt.storage is None

    await rt.start()

    assert rt._started is True
    assert rt.storage is not None
    assert rt.storage.conn is not None

    await rt.stop()

    assert rt._started is False
    assert rt.storage.conn is None


@pytest.mark.asyncio
async def test_add_bot(runtime):
    data = _make_session_data(1)
    bot = await runtime.add_bot(data, BotConfig(api_id=12345))

    assert isinstance(bot, BotHandle)
    assert bot.bot_id == 1
    assert 1 in runtime.bots
    assert runtime.bots[1] is bot


@pytest.mark.asyncio
async def test_add_duplicate_bot_raises(runtime):
    data = _make_session_data(1)
    await runtime.add_bot(data, BotConfig(api_id=12345))

    with pytest.raises(ValueError, match="already registered"):
        await runtime.add_bot(_make_session_data(1), BotConfig(api_id=12345))


@pytest.mark.asyncio
async def test_remove_bot(runtime):
    data = _make_session_data(1)
    await runtime.add_bot(data, BotConfig(api_id=12345))
    assert 1 in runtime.bots

    await runtime.remove_bot(1)
    assert 1 not in runtime.bots


@pytest.mark.asyncio
async def test_remove_nonexistent_bot_raises(runtime):
    with pytest.raises(KeyError, match="not found"):
        await runtime.remove_bot(999)


@pytest.mark.asyncio
async def test_add_bot_after_stop_raises(storage_path):
    rt = Runtime(storage_path=storage_path, **RUNTIME_KWARGS)
    await rt.start()
    await rt.stop()

    with pytest.raises(RuntimeError, match="not started"):
        await rt.add_bot(_make_session_data(1), BotConfig(api_id=12345))


@pytest.mark.asyncio
async def test_runtime_metrics(runtime):
    assert runtime.metrics.total_bots == 0

    await runtime.add_bot(_make_session_data(1), BotConfig(api_id=1))
    assert runtime.metrics.total_bots == 1

    await runtime.add_bot(_make_session_data(2), BotConfig(api_id=1))
    assert runtime.metrics.total_bots == 2

    await runtime.remove_bot(1)
    assert runtime.metrics.total_bots == 1


@pytest.mark.asyncio
async def test_async_context_manager(storage_path):
    async with Runtime(storage_path=storage_path, **RUNTIME_KWARGS) as rt:
        assert rt._started is True
        bot = await rt.add_bot(_make_session_data(1), BotConfig(api_id=1))
        assert 1 in rt.bots

    # After exiting the context, runtime should be stopped
    assert rt._started is False


@pytest.mark.asyncio
async def test_auth_key_index(runtime):
    data = _make_session_data(1, auth_key=TEST_AUTH_KEY)
    bot = await runtime.add_bot(data, BotConfig(api_id=12345))

    assert bot.auth_key_id != b""

    found = runtime.get_bot_by_auth_key_id(bot.auth_key_id)
    assert found is bot

    # Non-existent auth_key_id returns None
    assert runtime.get_bot_by_auth_key_id(b"\x00" * 8) is None

    # After removal, auth key index is cleaned up
    await runtime.remove_bot(1)
    assert runtime.get_bot_by_auth_key_id(bot.auth_key_id) is None
