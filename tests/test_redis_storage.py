"""Comprehensive tests for RedisStorage.

redis and msgpack are optional dependencies, so we mock them entirely.
All async Redis interactions are driven through a mock ``redis.asyncio`` client.
"""

import sys
import sqlite3
import types
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
import pytest_asyncio

from pyrogram.storage.session_data import SessionData


# ---------------------------------------------------------------------------
# Mock helpers for msgpack and redis.asyncio
# ---------------------------------------------------------------------------

def _fake_packb(obj, *, use_bin_type=True):
    """Trivial serialiser: use repr() so round-trips are deterministic."""
    import pickle
    return pickle.dumps(obj)


def _fake_unpackb(data, *, raw=False):
    import pickle
    return pickle.loads(data)


@pytest.fixture(autouse=True)
def _mock_msgpack(monkeypatch):
    """Inject a fake ``msgpack`` module into sys.modules for the test run."""
    fake = types.ModuleType("msgpack")
    fake.packb = _fake_packb
    fake.unpackb = _fake_unpackb
    monkeypatch.setitem(sys.modules, "msgpack", fake)
    return fake


# ---------------------------------------------------------------------------
# AsyncMock pipeline context-manager helper
# ---------------------------------------------------------------------------

class FakePipeline:
    """Mimics ``async with redis.pipeline(...) as pipe:``."""

    def __init__(self):
        self.hset = MagicMock()
        self.sadd = MagicMock()
        self.delete = MagicMock()
        self.srem = MagicMock()
        self.hgetall = MagicMock()
        self.execute = AsyncMock(return_value=[])

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        pass


def _make_mock_redis():
    """Return a fully-wired ``AsyncMock`` standing in for an aioredis client."""
    mock = AsyncMock()
    mock.ping = AsyncMock()
    mock.aclose = AsyncMock()
    mock.hset = AsyncMock()
    mock.hget = AsyncMock(return_value=None)
    mock.hgetall = AsyncMock(return_value={})
    mock.hdel = AsyncMock()
    mock.sadd = AsyncMock()
    mock.srem = AsyncMock()
    mock.smembers = AsyncMock(return_value=set())

    # pipeline() must return something usable as ``async with ... as pipe:``
    _pipe = FakePipeline()
    mock.pipeline = MagicMock(return_value=_pipe)
    mock._pipe = _pipe  # stash for assertions
    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_redis():
    return _make_mock_redis()


@pytest_asyncio.fixture
async def storage(mock_redis, monkeypatch):
    """Provide a *connected* ``RedisStorage`` backed by the mock client."""
    # Patch redis.asyncio so the import inside open() succeeds
    fake_aioredis = types.ModuleType("redis.asyncio")
    fake_aioredis.from_url = MagicMock(return_value=mock_redis)
    monkeypatch.setitem(sys.modules, "redis", types.ModuleType("redis"))
    monkeypatch.setitem(sys.modules, "redis.asyncio", fake_aioredis)

    from pyrogram.storage.redis_storage import RedisStorage

    s = RedisStorage(uri="redis://localhost:6379/0")
    await s.open()
    yield s
    # Don't call close here — some tests exercise close() explicitly.


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


def _packed(value):
    """Shorthand: pack a value the same way RedisStorage does."""
    return _fake_packb(value, use_bin_type=True)


def _session_hash(data: SessionData) -> dict:
    """Build the raw Redis hash dict that ``hgetall`` would return."""
    return {
        b"bot_id": _packed(data.bot_id),
        b"dc_id": _packed(data.dc_id),
        b"server_address": _packed(data.server_address),
        b"port": _packed(data.port),
        b"api_id": _packed(data.api_id),
        b"test_mode": _packed(data.test_mode),
        b"auth_key": _packed(data.auth_key),
        b"date": _packed(data.date),
        b"user_id": _packed(data.user_id),
        b"is_bot": _packed(data.is_bot),
    }


# ===================================================================
# 1. open / close
# ===================================================================

class TestOpenClose:
    @pytest.mark.asyncio
    async def test_open_connects_and_pings(self, storage, mock_redis):
        mock_redis.ping.assert_awaited_once()
        assert storage._redis is mock_redis

    @pytest.mark.asyncio
    async def test_open_raises_on_missing_redis(self, monkeypatch):
        """If redis is not installed, open() should raise ImportError."""
        # Remove redis.asyncio from sys.modules so the import fails
        monkeypatch.delitem(sys.modules, "redis.asyncio", raising=False)
        monkeypatch.delitem(sys.modules, "redis", raising=False)

        from pyrogram.storage.redis_storage import RedisStorage

        s = RedisStorage()
        with pytest.raises(ImportError, match="redis is required"):
            await s.open()

    @pytest.mark.asyncio
    async def test_close_calls_aclose(self, storage, mock_redis):
        await storage.close()
        mock_redis.aclose.assert_awaited_once()
        assert storage._redis is None

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self, storage, mock_redis):
        await storage.close()
        await storage.close()  # should not raise
        # aclose called only once (second close sees _redis is None)
        mock_redis.aclose.assert_awaited_once()


# ===================================================================
# 2. save_session
# ===================================================================

class TestSaveSession:
    @pytest.mark.asyncio
    async def test_save_session_uses_pipeline(self, storage, mock_redis):
        data = _make_session(42)
        await storage.save_session(data)

        pipe = mock_redis._pipe
        pipe.hset.assert_called_once()
        pipe.sadd.assert_called_once()
        pipe.execute.assert_awaited_once()

        # Verify the key used
        hset_args = pipe.hset.call_args
        assert hset_args[0][0] == "kuri:session:42"

        # Verify bot_id is added to the all-bots set
        sadd_args = pipe.sadd.call_args
        assert sadd_args[0] == ("kuri:bots", b"42")

    @pytest.mark.asyncio
    async def test_save_session_packs_all_fields(self, storage, mock_redis):
        data = _make_session(7, dc_id=3, port=8443, api_id=999)
        await storage.save_session(data)

        pipe = mock_redis._pipe
        mapping = pipe.hset.call_args[1]["mapping"]
        assert b"bot_id" in mapping
        assert b"dc_id" in mapping
        assert b"server_address" in mapping
        assert b"port" in mapping
        assert b"api_id" in mapping
        assert b"test_mode" in mapping
        assert b"auth_key" in mapping
        assert b"date" in mapping
        assert b"user_id" in mapping
        assert b"is_bot" in mapping

        # Verify packed values round-trip correctly
        assert _fake_unpackb(mapping[b"dc_id"]) == 3
        assert _fake_unpackb(mapping[b"port"]) == 8443
        assert _fake_unpackb(mapping[b"api_id"]) == 999


# ===================================================================
# 3. read_session
# ===================================================================

class TestReadSession:
    @pytest.mark.asyncio
    async def test_read_session_returns_data(self, storage, mock_redis):
        data = _make_session(100, dc_id=5, api_id=777)
        mock_redis.hgetall.return_value = _session_hash(data)

        result = await storage.read_session(100)

        assert result is not None
        assert result.bot_id == 100
        assert result.dc_id == 5
        assert result.api_id == 777
        assert result.server_address == "149.154.167.51"
        assert result.port == 443
        assert result.auth_key == b"\xab" * 256
        assert result.is_bot is True

    @pytest.mark.asyncio
    async def test_read_session_returns_none_when_missing(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {}
        result = await storage.read_session(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_read_session_uses_correct_key(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {}
        await storage.read_session(42)
        mock_redis.hgetall.assert_awaited_with("kuri:session:42")

    @pytest.mark.asyncio
    async def test_read_session_defaults_for_missing_fields(self, storage, mock_redis):
        """If some fields are absent from the hash, defaults kick in."""
        mock_redis.hgetall.return_value = {
            b"bot_id": _packed(55),
        }
        result = await storage.read_session(55)
        assert result.bot_id == 55
        assert result.dc_id == 2            # default
        assert result.server_address == "149.154.167.51"  # default
        assert result.port == 443           # default
        assert result.test_mode is False    # default
        assert result.date == 0             # default
        assert result.api_id is None        # default
        assert result.auth_key is None      # default
        assert result.user_id is None       # default
        assert result.is_bot is None        # default


# ===================================================================
# 4. read_all_sessions
# ===================================================================

class TestReadAllSessions:
    @pytest.mark.asyncio
    async def test_read_all_sessions_empty(self, storage, mock_redis):
        mock_redis.smembers.return_value = set()
        result = await storage.read_all_sessions()
        assert result == []

    @pytest.mark.asyncio
    async def test_read_all_sessions_returns_multiple(self, storage, mock_redis):
        mock_redis.smembers.return_value = {b"1", b"2"}

        data1 = _make_session(1, dc_id=1)
        data2 = _make_session(2, dc_id=2)

        pipe = mock_redis._pipe
        pipe.execute.return_value = [_session_hash(data1), _session_hash(data2)]

        result = await storage.read_all_sessions()
        assert len(result) == 2
        bot_ids = {s.bot_id for s in result}
        assert bot_ids == {1, 2}

    @pytest.mark.asyncio
    async def test_read_all_sessions_skips_empty_hashes(self, storage, mock_redis):
        mock_redis.smembers.return_value = {b"1", b"2"}

        data1 = _make_session(1)
        pipe = mock_redis._pipe
        pipe.execute.return_value = [_session_hash(data1), {}]

        result = await storage.read_all_sessions()
        assert len(result) == 1
        assert result[0].bot_id == 1


# ===================================================================
# 5. delete_session
# ===================================================================

class TestDeleteSession:
    @pytest.mark.asyncio
    async def test_delete_session_removes_all_keys(self, storage, mock_redis):
        await storage.delete_session(42)

        pipe = mock_redis._pipe
        assert pipe.delete.call_count == 4

        deleted_keys = [c[0][0] for c in pipe.delete.call_args_list]
        assert "kuri:session:42" in deleted_keys
        assert "kuri:peers:42" in deleted_keys
        assert "kuri:usernames:42" in deleted_keys
        assert "kuri:ustate:42" in deleted_keys

        pipe.srem.assert_called_once_with("kuri:bots", b"42")
        pipe.execute.assert_awaited_once()


# ===================================================================
# 6. get_session_field / set_session_field
# ===================================================================

class TestSessionField:
    @pytest.mark.asyncio
    async def test_get_session_field_returns_unpacked_value(self, storage, mock_redis):
        mock_redis.hget.return_value = _packed(42)
        result = await storage.get_session_field(10, "dc_id")
        assert result == 42
        mock_redis.hget.assert_awaited_with("kuri:session:10", b"dc_id")

    @pytest.mark.asyncio
    async def test_get_session_field_returns_none_for_missing(self, storage, mock_redis):
        mock_redis.hget.return_value = None
        result = await storage.get_session_field(10, "auth_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_session_field(self, storage, mock_redis):
        await storage.set_session_field(10, "dc_id", 5)
        mock_redis.hset.assert_awaited_once()
        args = mock_redis.hset.call_args
        assert args[0][0] == "kuri:session:10"
        assert args[0][1] == b"dc_id"
        assert _fake_unpackb(args[0][2]) == 5

    @pytest.mark.asyncio
    async def test_set_session_field_string_value(self, storage, mock_redis):
        await storage.set_session_field(10, "server_address", "10.0.0.1")
        args = mock_redis.hset.call_args
        assert _fake_unpackb(args[0][2]) == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_set_session_field_bytes_value(self, storage, mock_redis):
        key_bytes = b"\x00" * 256
        await storage.set_session_field(10, "auth_key", key_bytes)
        args = mock_redis.hset.call_args
        assert _fake_unpackb(args[0][2]) == key_bytes


# ===================================================================
# 7. update_peers
# ===================================================================

class TestUpdatePeers:
    @pytest.mark.asyncio
    async def test_update_peers_stores_packed_data(self, storage, mock_redis):
        peers = [
            (111, 0xABC, "user", "1234567890"),
            (222, 0xDEF, "bot", None),
        ]
        await storage.update_peers(10, peers)

        mock_redis.hset.assert_awaited_once()
        args = mock_redis.hset.call_args
        assert args[0][0] == "kuri:peers:10"

        mapping = args[1]["mapping"]
        assert b"111" in mapping
        assert b"222" in mapping

        # Verify packed contents (peer_id, access_hash, type, phone, timestamp)
        unpacked = _fake_unpackb(mapping[b"111"])
        assert unpacked[0] == 111
        assert unpacked[1] == 0xABC
        assert unpacked[2] == "user"
        assert unpacked[3] == "1234567890"
        assert isinstance(unpacked[4], int)  # timestamp

    @pytest.mark.asyncio
    async def test_update_peers_empty_list_is_noop(self, storage, mock_redis):
        await storage.update_peers(10, [])
        mock_redis.hset.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_peers_includes_timestamp(self, storage, mock_redis):
        import time

        before = int(time.time())
        await storage.update_peers(10, [(1, 2, "user", None)])
        after = int(time.time())

        mapping = mock_redis.hset.call_args[1]["mapping"]
        unpacked = _fake_unpackb(mapping[b"1"])
        assert before <= unpacked[4] <= after


# ===================================================================
# 8. update_usernames
# ===================================================================

class TestUpdateUsernames:
    @pytest.mark.asyncio
    async def test_update_usernames_stores_packed_peer_ids(self, storage, mock_redis):
        usernames = [(111, ["Alice", "alice_alt"])]
        await storage.update_usernames(10, usernames)

        mock_redis.hset.assert_awaited_once()
        args = mock_redis.hset.call_args
        assert args[0][0] == "kuri:usernames:10"

        mapping = args[1]["mapping"]
        # Usernames should be lowercased
        assert b"alice" in mapping
        assert b"alice_alt" in mapping
        # Both point to peer_id 111
        assert _fake_unpackb(mapping[b"alice"]) == 111
        assert _fake_unpackb(mapping[b"alice_alt"]) == 111

    @pytest.mark.asyncio
    async def test_update_usernames_empty_list_is_noop(self, storage, mock_redis):
        await storage.update_usernames(10, [])
        mock_redis.hset.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_usernames_lowercases(self, storage, mock_redis):
        usernames = [(1, ["FOO_BAR"])]
        await storage.update_usernames(10, usernames)

        mapping = mock_redis.hset.call_args[1]["mapping"]
        assert b"foo_bar" in mapping
        assert b"FOO_BAR" not in mapping

    @pytest.mark.asyncio
    async def test_update_usernames_multiple_peers(self, storage, mock_redis):
        usernames = [
            (100, ["user_a"]),
            (200, ["user_b", "user_b_alt"]),
        ]
        await storage.update_usernames(10, usernames)

        mapping = mock_redis.hset.call_args[1]["mapping"]
        assert _fake_unpackb(mapping[b"user_a"]) == 100
        assert _fake_unpackb(mapping[b"user_b"]) == 200
        assert _fake_unpackb(mapping[b"user_b_alt"]) == 200


# ===================================================================
# 9. get_peer_by_id
# ===================================================================

class TestGetPeerById:
    @pytest.mark.asyncio
    async def test_get_peer_by_id_found(self, storage, mock_redis):
        peer_data = (111, 0xABC, "user", "123", 1700000000)
        mock_redis.hget.return_value = _packed(peer_data)

        result = await storage.get_peer_by_id(10, 111)

        assert result == peer_data
        mock_redis.hget.assert_awaited_with("kuri:peers:10", b"111")

    @pytest.mark.asyncio
    async def test_get_peer_by_id_not_found(self, storage, mock_redis):
        mock_redis.hget.return_value = None
        result = await storage.get_peer_by_id(10, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_peer_by_id_returns_tuple(self, storage, mock_redis):
        peer_data = [111, 0xABC, "user", None, 1700000000]
        mock_redis.hget.return_value = _packed(peer_data)

        result = await storage.get_peer_by_id(10, 111)
        assert isinstance(result, tuple)


# ===================================================================
# 10. get_peer_by_username
# ===================================================================

class TestGetPeerByUsername:
    @pytest.mark.asyncio
    async def test_get_peer_by_username_found(self, storage, mock_redis):
        peer_data = (111, 0xABC, "user", "123", 1700000000)

        # First hget returns the peer_id for the username
        # Second hget returns the peer data
        mock_redis.hget.side_effect = [
            _packed(111),       # username -> peer_id
            _packed(peer_data), # peer_id -> data
        ]

        result = await storage.get_peer_by_username(10, "alice")
        assert result == peer_data

        # Verify username was lowercased
        first_call = mock_redis.hget.call_args_list[0]
        assert first_call[0] == ("kuri:usernames:10", b"alice")

    @pytest.mark.asyncio
    async def test_get_peer_by_username_not_found(self, storage, mock_redis):
        mock_redis.hget.return_value = None
        result = await storage.get_peer_by_username(10, "nobody")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_peer_by_username_case_insensitive(self, storage, mock_redis):
        mock_redis.hget.side_effect = [
            _packed(111),
            _packed((111, 0xABC, "user", None, 1700000000)),
        ]

        await storage.get_peer_by_username(10, "ALICE")
        first_call = mock_redis.hget.call_args_list[0]
        assert first_call[0][1] == b"alice"

    @pytest.mark.asyncio
    async def test_get_peer_by_username_peer_deleted(self, storage, mock_redis):
        """Username exists but peer data was deleted."""
        mock_redis.hget.side_effect = [
            _packed(111),  # username -> peer_id
            None,          # peer data missing
        ]
        result = await storage.get_peer_by_username(10, "ghost")
        assert result is None


# ===================================================================
# 11. get_peer_by_phone_number
# ===================================================================

class TestGetPeerByPhoneNumber:
    @pytest.mark.asyncio
    async def test_get_peer_by_phone_found(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {
            b"111": _packed((111, 0xABC, "user", "5551234567", 1700000000)),
            b"222": _packed((222, 0xDEF, "user", "5559999999", 1700000000)),
        }

        result = await storage.get_peer_by_phone_number(10, "5551234567")
        assert result is not None
        assert result[0] == 111
        assert result[3] == "5551234567"

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_not_found(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {
            b"111": _packed((111, 0xABC, "user", "5551234567", 1700000000)),
        }
        result = await storage.get_peer_by_phone_number(10, "0000000000")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_empty_peers(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {}
        result = await storage.get_peer_by_phone_number(10, "5551234567")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_with_none_phone_fields(self, storage, mock_redis):
        """Peers with None phone numbers should not match."""
        mock_redis.hgetall.return_value = {
            b"111": _packed((111, 0xABC, "user", None, 1700000000)),
            b"222": _packed((222, 0xDEF, "user", "5551234567", 1700000000)),
        }
        result = await storage.get_peer_by_phone_number(10, "5551234567")
        assert result[0] == 222

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_returns_first_match(self, storage, mock_redis):
        """If multiple peers share a phone, the scan returns whichever comes first."""
        mock_redis.hgetall.return_value = {
            b"111": _packed((111, 0xABC, "user", "5551234567", 1700000000)),
        }
        result = await storage.get_peer_by_phone_number(10, "5551234567")
        assert result is not None
        assert isinstance(result, tuple)


# ===================================================================
# 12. update_state
# ===================================================================

class TestUpdateState:
    @pytest.mark.asyncio
    async def test_read_state_empty(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {}
        result = await storage.update_state(10)  # value=object => read
        assert result == []

    @pytest.mark.asyncio
    async def test_read_state_returns_sorted(self, storage, mock_redis):
        mock_redis.hgetall.return_value = {
            b"1": _packed((1, 100, 50, 999, 7)),
            b"2": _packed((2, 200, 60, 500, 8)),
        }
        result = await storage.update_state(10)
        assert len(result) == 2
        # Sorted by date (index 3): 500 < 999
        assert result[0][3] == 500
        assert result[1][3] == 999

    @pytest.mark.asyncio
    async def test_read_state_with_none_date(self, storage, mock_redis):
        """States with None date should sort as 0."""
        mock_redis.hgetall.return_value = {
            b"1": _packed((1, 100, 50, None, 7)),
            b"2": _packed((2, 200, 60, 500, 8)),
        }
        result = await storage.update_state(10)
        # None date sorts as 0, before 500
        assert result[0][0] == 1
        assert result[1][0] == 2

    @pytest.mark.asyncio
    async def test_write_state_new(self, storage, mock_redis):
        """Writing a new state (no existing entry)."""
        mock_redis.hget.return_value = None
        state_val = (1, 100, 50, 999, 7)
        await storage.update_state(10, state_val)

        mock_redis.hset.assert_awaited_once()
        args = mock_redis.hset.call_args
        assert args[0][0] == "kuri:ustate:10"
        assert args[0][1] == b"1"
        assert _fake_unpackb(args[0][2]) == state_val

    @pytest.mark.asyncio
    async def test_write_state_merge_existing(self, storage, mock_redis):
        """Writing with partial None values should merge with existing."""
        existing = (1, 100, 50, 999, 7)
        mock_redis.hget.return_value = _packed(existing)

        # Update only pts (index 1) — others are None so they keep existing values
        new_val = (1, 200, None, None, None)
        await storage.update_state(10, new_val)

        args = mock_redis.hset.call_args
        merged = _fake_unpackb(args[0][2])
        assert merged == (1, 200, 50, 999, 7)

    @pytest.mark.asyncio
    async def test_write_state_full_overwrite(self, storage, mock_redis):
        """Writing with all non-None values should overwrite all fields."""
        existing = (1, 100, 50, 999, 7)
        mock_redis.hget.return_value = _packed(existing)

        new_val = (1, 200, 60, 888, 8)
        await storage.update_state(10, new_val)

        args = mock_redis.hset.call_args
        merged = _fake_unpackb(args[0][2])
        assert merged == (1, 200, 60, 888, 8)

    @pytest.mark.asyncio
    async def test_delete_state_by_id(self, storage, mock_redis):
        await storage.update_state(10, 5)  # int => delete
        mock_redis.hdel.assert_awaited_once_with("kuri:ustate:10", b"5")

    @pytest.mark.asyncio
    async def test_write_state_with_list(self, storage, mock_redis):
        """Lists should be accepted in addition to tuples."""
        mock_redis.hget.return_value = None
        await storage.update_state(10, [1, 100, 50, 999, 7])
        mock_redis.hset.assert_awaited_once()


# ===================================================================
# 13. migrate_from_file
# ===================================================================

class TestMigrateFromFile:
    @pytest.mark.asyncio
    async def test_migrate_from_file_basic(self, storage, mock_redis, tmp_path):
        """Migrate a minimal SQLite session file."""
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER,
                api_id INTEGER,
                server_address TEXT,
                port INTEGER,
                test_mode INTEGER,
                auth_key BLOB,
                date INTEGER,
                user_id INTEGER,
                is_bot INTEGER
            )
        """)
        conn.execute(
            "INSERT INTO sessions VALUES (2, 12345, '149.154.167.51', 443, 0, ?, 1000, 99, 1)",
            (b"\xab" * 256,),
        )
        conn.commit()
        conn.close()

        # Need a fresh pipeline for each call
        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)
        mock_redis.hget.return_value = None  # no existing update_state

        result = await storage.migrate_from_file(db_path, bot_id=99)

        assert result is not None
        assert result.bot_id == 99
        assert result.dc_id == 2
        assert result.api_id == 12345
        assert result.auth_key == b"\xab" * 256
        assert result.is_bot is True

    @pytest.mark.asyncio
    async def test_migrate_from_file_with_peers(self, storage, mock_redis, tmp_path):
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER, api_id INTEGER, server_address TEXT,
                port INTEGER, test_mode INTEGER, auth_key BLOB,
                date INTEGER, user_id INTEGER, is_bot INTEGER
            )
        """)
        conn.execute(
            "INSERT INTO sessions VALUES (2, 12345, '1.2.3.4', 443, 0, ?, 0, 99, 1)",
            (b"\x00" * 256,),
        )
        conn.execute("""
            CREATE TABLE peers (
                id INTEGER, access_hash INTEGER, type TEXT, phone_number TEXT
            )
        """)
        conn.execute("INSERT INTO peers VALUES (111, 12345, 'user', '5551234567')")
        conn.execute("INSERT INTO peers VALUES (222, 67890, 'bot', NULL)")
        conn.commit()
        conn.close()

        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)
        mock_redis.hget.return_value = None

        result = await storage.migrate_from_file(db_path, bot_id=99)
        assert result is not None

        # update_peers should have been called with the peers
        # (The mock_redis.hset calls include both the session save and peers)
        assert mock_redis.hset.await_count >= 1

    @pytest.mark.asyncio
    async def test_migrate_from_file_with_usernames(self, storage, mock_redis, tmp_path):
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER, api_id INTEGER, server_address TEXT,
                port INTEGER, test_mode INTEGER, auth_key BLOB,
                date INTEGER, user_id INTEGER, is_bot INTEGER
            )
        """)
        conn.execute(
            "INSERT INTO sessions VALUES (2, 12345, '1.2.3.4', 443, 0, ?, 0, 99, 1)",
            (b"\x00" * 256,),
        )
        conn.execute("""
            CREATE TABLE usernames (
                peer_id INTEGER, username TEXT
            )
        """)
        conn.execute("INSERT INTO usernames VALUES (111, 'alice')")
        conn.execute("INSERT INTO usernames VALUES (111, 'alice_v2')")
        conn.execute("INSERT INTO usernames VALUES (222, 'bob')")
        conn.commit()
        conn.close()

        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)
        mock_redis.hget.return_value = None

        result = await storage.migrate_from_file(db_path, bot_id=99)
        assert result is not None

    @pytest.mark.asyncio
    async def test_migrate_from_file_with_update_state(self, storage, mock_redis, tmp_path):
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER, api_id INTEGER, server_address TEXT,
                port INTEGER, test_mode INTEGER, auth_key BLOB,
                date INTEGER, user_id INTEGER, is_bot INTEGER
            )
        """)
        conn.execute(
            "INSERT INTO sessions VALUES (2, 12345, '1.2.3.4', 443, 0, ?, 0, 99, 1)",
            (b"\x00" * 256,),
        )
        conn.execute("""
            CREATE TABLE update_state (
                id INTEGER, pts INTEGER, qts INTEGER, date INTEGER, seq INTEGER
            )
        """)
        conn.execute("INSERT INTO update_state VALUES (1, 100, 50, 999, 7)")
        conn.commit()
        conn.close()

        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)
        mock_redis.hget.return_value = None  # no existing state for merge

        result = await storage.migrate_from_file(db_path, bot_id=99)
        assert result is not None

        # update_state should have written via hset
        hset_calls = mock_redis.hset.call_args_list
        # At least one call for update_state
        ustate_calls = [c for c in hset_calls if "kuri:ustate:" in str(c)]
        assert len(ustate_calls) >= 1

    @pytest.mark.asyncio
    async def test_migrate_from_file_invalid_path(self, storage, mock_redis):
        result = await storage.migrate_from_file("/nonexistent/path.db", bot_id=99)
        assert result is None

    @pytest.mark.asyncio
    async def test_migrate_from_file_empty_sessions(self, storage, mock_redis, tmp_path):
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER, api_id INTEGER, server_address TEXT,
                port INTEGER, test_mode INTEGER, auth_key BLOB,
                date INTEGER, user_id INTEGER, is_bot INTEGER
            )
        """)
        conn.commit()
        conn.close()

        result = await storage.migrate_from_file(db_path, bot_id=99)
        assert result is None

    @pytest.mark.asyncio
    async def test_migrate_from_file_missing_optional_tables(self, storage, mock_redis, tmp_path):
        """Migrate should succeed even without peers/usernames/update_state tables."""
        db_path = str(tmp_path / "session.session")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE sessions (
                dc_id INTEGER, api_id INTEGER, server_address TEXT,
                port INTEGER, test_mode INTEGER, auth_key BLOB,
                date INTEGER, user_id INTEGER, is_bot INTEGER
            )
        """)
        conn.execute(
            "INSERT INTO sessions VALUES (2, 12345, '1.2.3.4', 443, 0, ?, 0, 99, 1)",
            (b"\x00" * 256,),
        )
        conn.commit()
        conn.close()

        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)

        result = await storage.migrate_from_file(db_path, bot_id=99)
        assert result is not None
        assert result.bot_id == 99


# ===================================================================
# 14. Key prefix helpers
# ===================================================================

class TestKeyHelpers:
    def test_session_key(self, storage):
        assert storage._session_key(42) == "kuri:session:42"

    def test_peers_key(self, storage):
        assert storage._peers_key(42) == "kuri:peers:42"

    def test_usernames_key(self, storage):
        assert storage._usernames_key(42) == "kuri:usernames:42"

    def test_ustate_key(self, storage):
        assert storage._ustate_key(42) == "kuri:ustate:42"


# ===================================================================
# 15. Pack / Unpack
# ===================================================================

class TestPackUnpack:
    def test_round_trip_int(self, storage):
        assert storage._unpack(storage._pack(42)) == 42

    def test_round_trip_string(self, storage):
        assert storage._unpack(storage._pack("hello")) == "hello"

    def test_round_trip_bytes(self, storage):
        data = b"\x00\xff" * 128
        assert storage._unpack(storage._pack(data)) == data

    def test_round_trip_none(self, storage):
        assert storage._unpack(storage._pack(None)) is None

    def test_round_trip_bool(self, storage):
        assert storage._unpack(storage._pack(True)) is True
        assert storage._unpack(storage._pack(False)) is False

    def test_round_trip_tuple(self, storage):
        # msgpack converts tuples to lists; our fake preserves them
        val = (1, 2, "x", None)
        result = storage._unpack(storage._pack(val))
        assert tuple(result) == val

    def test_round_trip_nested(self, storage):
        val = {"key": [1, 2, 3], "other": "value"}
        assert storage._unpack(storage._pack(val)) == val


# ===================================================================
# 16. _session_from_hash
# ===================================================================

class TestSessionFromHash:
    def test_full_hash(self, storage):
        data = _make_session(42, dc_id=3, api_id=999)
        raw = _session_hash(data)
        result = storage._session_from_hash(raw)
        assert result.bot_id == 42
        assert result.dc_id == 3
        assert result.api_id == 999
        assert result.server_address == "149.154.167.51"
        assert result.port == 443
        assert result.is_bot is True

    def test_partial_hash_uses_defaults(self, storage):
        """Missing fields should use the documented defaults."""
        raw = {b"bot_id": _packed(55)}
        result = storage._session_from_hash(raw)
        assert result.bot_id == 55
        assert result.dc_id == 2
        assert result.server_address == "149.154.167.51"
        assert result.port == 443
        assert result.test_mode is False
        assert result.date == 0

    def test_empty_hash_uses_all_defaults(self, storage):
        result = storage._session_from_hash({})
        assert result.bot_id == 0
        assert result.dc_id == 2
        assert result.server_address == "149.154.167.51"
        assert result.port == 443
        assert result.api_id is None
        assert result.auth_key is None
        assert result.user_id is None
        assert result.is_bot is None


# ===================================================================
# 17. Constructor
# ===================================================================

class TestConstructor:
    def test_default_uri(self):
        from pyrogram.storage.redis_storage import RedisStorage
        s = RedisStorage()
        assert s._uri == "redis://localhost:6379/0"
        assert s._redis is None

    def test_custom_uri(self):
        from pyrogram.storage.redis_storage import RedisStorage
        s = RedisStorage(uri="redis://myhost:1234/3")
        assert s._uri == "redis://myhost:1234/3"


# ===================================================================
# 18. Edge cases
# ===================================================================

class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_update_peers_single_peer(self, storage, mock_redis):
        peers = [(1, 0, "user", None)]
        await storage.update_peers(10, peers)
        mock_redis.hset.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_usernames_empty_username_list_per_peer(self, storage, mock_redis):
        """A peer with an empty username list produces an empty mapping but still calls hset."""
        usernames = [(111, [])]
        await storage.update_usernames(10, usernames)
        # The outer list is non-empty so the early return is not hit;
        # hset is called with an empty mapping dict.
        mock_redis.hset.assert_awaited_once()
        mapping = mock_redis.hset.call_args[1]["mapping"]
        assert mapping == {}

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_short_tuple(self, storage, mock_redis):
        """Peers with fewer than 4 elements should not match."""
        mock_redis.hgetall.return_value = {
            b"111": _packed((111, 0xABC, "user")),  # only 3 elements
        }
        result = await storage.get_peer_by_phone_number(10, "5551234567")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_session_with_none_auth_key(self, storage, mock_redis):
        data = _make_session(1, auth_key=None)
        await storage.save_session(data)
        pipe = mock_redis._pipe
        mapping = pipe.hset.call_args[1]["mapping"]
        assert _fake_unpackb(mapping[b"auth_key"]) is None

    @pytest.mark.asyncio
    async def test_delete_session_uses_pipeline(self, storage, mock_redis):
        """Verify that delete_session is done atomically via pipeline."""
        pipe = FakePipeline()
        mock_redis.pipeline = MagicMock(return_value=pipe)

        await storage.delete_session(42)
        pipe.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_state_read_returns_tuples(self, storage, mock_redis):
        """Each state entry should be a tuple, not a list."""
        mock_redis.hgetall.return_value = {
            b"1": _packed([1, 100, 50, 999, 7]),
        }
        result = await storage.update_state(10)
        assert len(result) == 1
        assert isinstance(result[0], tuple)

    @pytest.mark.asyncio
    async def test_update_state_write_with_tuple(self, storage, mock_redis):
        mock_redis.hget.return_value = None
        await storage.update_state(10, (1, 100, 50, 999, 7))
        mock_redis.hset.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_large_bot_id(self, storage, mock_redis):
        """Large bot IDs should be handled correctly."""
        large_id = 9999999999
        data = _make_session(large_id)
        await storage.save_session(data)
        pipe = mock_redis._pipe
        assert pipe.hset.call_args[0][0] == f"kuri:session:{large_id}"

    @pytest.mark.asyncio
    async def test_session_field_with_special_chars_in_value(self, storage, mock_redis):
        """Strings with special characters should be packed/unpacked correctly."""
        await storage.set_session_field(10, "server_address", "2001:db8::1")
        args = mock_redis.hset.call_args
        assert _fake_unpackb(args[0][2]) == "2001:db8::1"
