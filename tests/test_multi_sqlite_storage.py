import asyncio
import time

import pytest
import pytest_asyncio

from pyrogram.raw import types as raw_types
from pyrogram.storage.multi_sqlite_storage import MultiSQLiteStorage
from pyrogram.storage.session_data import SessionData
from pyrogram.storage.sqlite_storage import get_input_peer


@pytest_asyncio.fixture
async def storage(tmp_path):
    db_path = str(tmp_path / "multi.db")
    s = MultiSQLiteStorage(path=db_path, wal_autocheckpoint=1000)
    await s.open()
    yield s
    await s.close()


def _make_session(bot_id: int, **kwargs) -> SessionData:
    defaults = dict(
        dc_id=2,
        server_address="149.154.167.51",
        port=443,
        api_id=12345,
        test_mode=False,
        auth_key=b"\xab" * 256,
        date=1000000,
        user_id=bot_id,
        is_bot=True,
    )
    defaults.update(kwargs)
    return SessionData(bot_id=bot_id, **defaults)


async def _flush(storage: MultiSQLiteStorage) -> None:
    """Flush the batch writer by sending a sentinel and waiting for it to drain."""
    await storage._write_queue.put(None)
    if storage._writer_task:
        await storage._writer_task
    # Restart the writer for subsequent operations
    storage._closed = False
    storage._writer_task = asyncio.get_event_loop().create_task(storage._writer_loop())


# ---------- 1. open creates tables ----------

@pytest.mark.asyncio
async def test_open_creates_tables(storage):
    async with storage.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ) as cur:
        rows = await cur.fetchall()
    table_names = {r[0] for r in rows}
    assert {"sessions", "peers", "usernames", "update_state", "version"} <= table_names


# ---------- 2. save and read session ----------

@pytest.mark.asyncio
async def test_save_and_read_session(storage):
    data = _make_session(100, dc_id=3, api_id=9999, date=42)
    await storage.save_session(data)
    await _flush(storage)

    result = await storage.read_session(100)
    assert result is not None
    assert result.bot_id == 100
    assert result.dc_id == 3
    assert result.api_id == 9999
    assert result.date == 42
    assert result.auth_key == b"\xab" * 256
    assert result.is_bot is True


# ---------- 3. read all sessions ----------

@pytest.mark.asyncio
async def test_read_all_sessions(storage):
    for bot_id in (1, 2, 3):
        await storage.save_session(_make_session(bot_id))
    await _flush(storage)

    sessions = await storage.read_all_sessions()
    bot_ids = {s.bot_id for s in sessions}
    assert bot_ids == {1, 2, 3}


# ---------- 4. delete session ----------

@pytest.mark.asyncio
async def test_delete_session(storage):
    await storage.save_session(_make_session(500))
    await _flush(storage)

    assert await storage.read_session(500) is not None

    await storage.delete_session(500)
    await _flush(storage)

    assert await storage.read_session(500) is None


# ---------- 5. update peers and get_peer_by_id ----------

@pytest.mark.asyncio
async def test_update_peers(storage):
    await storage.save_session(_make_session(10))
    peers = [
        (111, 0xABC, "user", "1234567890"),
        (222, 0xDEF, "bot", None),
    ]
    await storage.update_peers(10, peers)
    await _flush(storage)

    peer = await storage.get_peer_by_id(10, 111)
    assert isinstance(peer, raw_types.InputPeerUser)
    assert peer.user_id == 111
    assert peer.access_hash == 0xABC

    peer2 = await storage.get_peer_by_id(10, 222)
    assert isinstance(peer2, raw_types.InputPeerUser)
    assert peer2.user_id == 222


# ---------- 6. get peer by username ----------

@pytest.mark.asyncio
async def test_get_peer_by_username(storage):
    await storage.save_session(_make_session(10))
    peers = [(111, 0xABC, "user", None)]
    await storage.update_peers(10, peers)
    await _flush(storage)

    # Manually set last_update_on to now so it's fresh
    await storage.conn.execute(
        "UPDATE peers SET last_update_on = ? WHERE bot_id = ? AND peer_id = ?",
        (int(time.time()), 10, 111),
    )
    await storage.conn.commit()

    usernames = [(111, ["alice", "alice_alt"])]
    await storage.update_usernames(10, usernames)
    await _flush(storage)

    peer = await storage.get_peer_by_username(10, "alice")
    assert isinstance(peer, raw_types.InputPeerUser)
    assert peer.user_id == 111

    peer_alt = await storage.get_peer_by_username(10, "alice_alt")
    assert peer_alt.user_id == 111


# ---------- 7. get peer by username expired ----------

@pytest.mark.asyncio
async def test_get_peer_by_username_expired(storage):
    await storage.save_session(_make_session(10))
    peers = [(111, 0xABC, "user", None)]
    await storage.update_peers(10, peers)
    await _flush(storage)

    # Set last_update_on to a time well beyond the 8-hour TTL
    old_time = int(time.time()) - (9 * 60 * 60)
    await storage.conn.execute(
        "UPDATE peers SET last_update_on = ? WHERE bot_id = ? AND peer_id = ?",
        (old_time, 10, 111),
    )
    await storage.conn.commit()

    usernames = [(111, ["stale_user"])]
    await storage.update_usernames(10, usernames)
    await _flush(storage)

    with pytest.raises(KeyError, match="Username expired"):
        await storage.get_peer_by_username(10, "stale_user")


# ---------- 8. get peer by phone number ----------

@pytest.mark.asyncio
async def test_get_peer_by_phone_number(storage):
    await storage.save_session(_make_session(10))
    peers = [(111, 0xABC, "user", "5551234567")]
    await storage.update_peers(10, peers)
    await _flush(storage)

    peer = await storage.get_peer_by_phone_number(10, "5551234567")
    assert isinstance(peer, raw_types.InputPeerUser)
    assert peer.user_id == 111


# ---------- 9. update state ----------

@pytest.mark.asyncio
async def test_update_state(storage):
    await storage.save_session(_make_session(10))

    # Set a state value: (id, pts, qts, date, seq)
    state_val = (1, 100, 50, 999999, 7)
    await storage.update_state(10, state_val)
    await _flush(storage)

    states = await storage.update_state(10)
    assert len(states) == 1
    assert states[0] == state_val

    # Delete state by id
    await storage.update_state(10, 1)
    await _flush(storage)

    states = await storage.update_state(10)
    assert len(states) == 0


# ---------- 10. batch writer ----------

@pytest.mark.asyncio
async def test_batch_writer(storage):
    # Enqueue many writes and verify all are committed after flushing
    for bot_id in range(1, 51):
        await storage.save_session(_make_session(bot_id))
    await _flush(storage)

    sessions = await storage.read_all_sessions()
    assert len(sessions) == 50


# ---------- 11. peer not found raises KeyError ----------

@pytest.mark.asyncio
async def test_peer_not_found_raises(storage):
    await storage.save_session(_make_session(10))
    await _flush(storage)

    with pytest.raises(KeyError, match="ID not found"):
        await storage.get_peer_by_id(10, 99999)


# ---------- 12. closed storage raises RuntimeError ----------

@pytest.mark.asyncio
async def test_closed_storage_raises(storage):
    await storage.close()

    with pytest.raises(RuntimeError, match="Storage is closed"):
        await storage.save_session(_make_session(999))
