import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from pyrogram.connection_manager import ConnectionManager, ManagedConnection, DC_FAILURE_THRESHOLD


def make_session():
    return SimpleNamespace(stop=AsyncMock())


def make_runtime():
    return SimpleNamespace()


@pytest.fixture
def cm():
    return ConnectionManager(runtime=make_runtime(), idle_timeout=60.0)


@pytest.mark.asyncio
async def test_register_session(cm):
    session = make_session()
    mc = await cm.register_session(bot_id=1, dc_id=2, session=session)

    assert isinstance(mc, ManagedConnection)
    assert mc.bot_id == 1
    assert mc.dc_id == 2
    assert mc.session is session
    assert mc.idle is False
    assert cm.connection_count() == 1
    assert cm.connection_count(dc_id=2) == 1


@pytest.mark.asyncio
async def test_remove_connection(cm):
    session = make_session()
    mc = await cm.register_session(bot_id=1, dc_id=2, session=session)
    assert cm.connection_count() == 1

    await cm.remove_connection(mc)
    assert cm.connection_count() == 0
    assert cm.connection_count(dc_id=2) == 0


@pytest.mark.asyncio
async def test_remove_bot(cm):
    s1 = make_session()
    s2 = make_session()
    s3 = make_session()

    mc1 = await cm.register_session(bot_id=10, dc_id=1, session=s1)
    mc2 = await cm.register_session(bot_id=10, dc_id=2, session=s2)
    # Different bot — should not be removed
    mc3 = await cm.register_session(bot_id=20, dc_id=1, session=s3)

    assert cm.connection_count() == 3

    removed = await cm.remove_bot(bot_id=10)
    assert len(removed) == 2
    assert mc1 in removed
    assert mc2 in removed
    assert mc3 not in removed
    assert cm.connection_count() == 1


@pytest.mark.asyncio
async def test_connection_count(cm):
    await cm.register_session(bot_id=1, dc_id=1, session=make_session())
    await cm.register_session(bot_id=2, dc_id=1, session=make_session())
    await cm.register_session(bot_id=1, dc_id=2, session=make_session())

    assert cm.connection_count() == 3
    assert cm.connection_count(dc_id=1) == 2
    assert cm.connection_count(dc_id=2) == 1
    assert cm.connection_count(dc_id=99) == 0


@pytest.mark.asyncio
async def test_mark_active_idle(cm):
    mc = await cm.register_session(bot_id=1, dc_id=1, session=make_session())
    assert mc.idle is False

    await cm.mark_idle(mc)
    assert mc.idle is True
    idle_time = mc.last_active

    await cm.mark_active(mc)
    assert mc.idle is False
    assert mc.last_active >= idle_time


@pytest.mark.asyncio
async def test_idle_reaper():
    cm = ConnectionManager(runtime=make_runtime(), idle_timeout=0.1)

    session = make_session()
    mc = await cm.register_session(bot_id=1, dc_id=1, session=session)
    await cm.mark_idle(mc)

    await cm.start()
    try:
        # Reaper sleeps for idle_timeout / 2 = 0.05s, then checks.
        # Wait long enough for at least one reap cycle.
        await asyncio.sleep(0.3)

        assert cm.connection_count() == 0
        session.stop.assert_awaited_once()
    finally:
        await cm.stop()


@pytest.mark.asyncio
async def test_dc_failure_coordination(cm):
    dc_id = 5
    bot_id = 1

    # Fire failures below threshold — should return 0.0
    for i in range(DC_FAILURE_THRESHOLD - 1):
        delay = await cm.on_connection_lost(dc_id, bot_id)
        assert delay == 0.0

    # One more failure should cross the threshold and return a positive backoff
    delay = await cm.on_connection_lost(dc_id, bot_id)
    assert delay > 0.0


@pytest.mark.asyncio
async def test_dc_cooldown(cm):
    dc_id = 3
    bot_id = 1

    # No failures yet — cooldown should be 0
    cooldown = await cm.get_dc_cooldown(dc_id)
    assert cooldown == 0.0

    # Trigger a failure burst
    for _ in range(DC_FAILURE_THRESHOLD):
        await cm.on_connection_lost(dc_id, bot_id)

    cooldown = await cm.get_dc_cooldown(dc_id)
    assert cooldown > 0.0
