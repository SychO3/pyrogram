import asyncio
import platform
import time
from hashlib import sha1
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyrogram.bot_handle import BotConfig, BotHandle, BotStorageProxy


def make_runtime(loop: asyncio.AbstractEventLoop) -> SimpleNamespace:
    return SimpleNamespace(
        loop=loop,
        proxy={"scheme": "socks5", "hostname": "127.0.0.1"},
        connection_factory=object(),
        protocol_factory=object(),
        handler_executor=object(),
        storage=MagicMock(),
        update_dispatcher=AsyncMock(),
    )


# ── BotConfig ──────────────────────────────────────────────────────────

class TestBotConfig:
    def test_bot_config_defaults(self):
        cfg = BotConfig(api_id=123)
        assert cfg.api_id == 123
        assert cfg.api_hash == ""
        assert cfg.device_model != ""
        assert cfg.system_version != ""
        assert platform.python_implementation() in cfg.device_model
        assert platform.system() in cfg.system_version
        assert cfg.system_lang_code == "en"
        assert cfg.lang_pack == ""
        assert cfg.lang_code == "en"
        assert cfg.init_connection_params is None
        assert cfg.no_updates is False
        assert cfg.skip_updates is False
        assert cfg.sleep_threshold == 10.0
        assert cfg.max_concurrent_transmissions == 3

    def test_bot_config_custom_device_model(self):
        cfg = BotConfig(api_id=1, device_model="CustomDevice", system_version="CustomOS")
        assert cfg.device_model == "CustomDevice"
        assert cfg.system_version == "CustomOS"


# ── BotHandle properties ───────────────────────────────────────────────

class TestBotHandleProperties:
    @pytest.mark.asyncio
    async def test_bot_handle_properties(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        config = BotConfig(api_id=42)
        auth_key = b"\xab" * 256
        bot = BotHandle(runtime, bot_id=100, config=config, auth_key=auth_key)

        # Delegated to runtime
        assert bot.loop is runtime.loop
        assert bot.proxy is runtime.proxy
        assert bot.connection_factory is runtime.connection_factory
        assert bot.protocol_factory is runtime.protocol_factory
        assert bot.executor is runtime.handler_executor

        # Delegated to config
        assert bot.app_version == config.app_version
        assert bot.device_model == config.device_model
        assert bot.system_version == config.system_version
        assert bot.system_lang_code == "en"
        assert bot.lang_pack == ""
        assert bot.lang_code == "en"
        assert bot.init_connection_params is None
        assert bot.no_updates is False
        assert bot.sleep_threshold == 10.0

    @pytest.mark.asyncio
    async def test_handle_name(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        bot = BotHandle(runtime, bot_id=7654321, config=BotConfig(api_id=1), auth_key=b"")

        assert bot.name == "7654321"
        assert bot.name == str(bot.bot_id)


# ── Auth key ───────────────────────────────────────────────────────────

class TestAuthKey:
    @pytest.mark.asyncio
    async def test_auth_key_id(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        auth_key = b"\x01\x02\x03" * 85 + b"\x01"  # 256 bytes
        bot = BotHandle(runtime, bot_id=1, config=BotConfig(api_id=1), auth_key=auth_key)

        expected = sha1(auth_key).digest()[-8:]
        assert bot.auth_key_id == expected
        assert len(bot.auth_key_id) == 8

    @pytest.mark.asyncio
    async def test_empty_auth_key(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        bot = BotHandle(runtime, bot_id=1, config=BotConfig(api_id=1), auth_key=b"")

        assert bot.auth_key_id == b""


# ── Server time ────────────────────────────────────────────────────────

class TestServerTime:
    @pytest.mark.asyncio
    async def test_server_time(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        bot = BotHandle(runtime, bot_id=1, config=BotConfig(api_id=1), auth_key=b"")

        # Initially close to time.time() (offset is 0)
        before = time.time()
        server_t = bot.server_time
        after = time.time()
        assert before <= server_t <= after

        # After _set_server_time, the offset shifts
        fake_server_ts = 1_700_000_000.0
        msg_id = int(fake_server_ts * (2**32))
        bot._set_server_time(msg_id)

        # server_time should now be roughly fake_server_ts
        result = bot.server_time
        assert abs(result - fake_server_ts) < 1.0


# ── BotStorageProxy ────────────────────────────────────────────────────

class TestBotStorageProxy:
    @pytest.mark.asyncio
    async def test_storage_proxy_get(self):
        storage = AsyncMock()
        storage.get_session_field = AsyncMock(return_value=2)
        proxy = BotStorageProxy(storage, bot_id=42)

        result = await proxy.dc_id()
        storage.get_session_field.assert_awaited_once_with(42, "dc_id")
        assert result == 2

    @pytest.mark.asyncio
    async def test_storage_proxy_set(self):
        storage = AsyncMock()
        proxy = BotStorageProxy(storage, bot_id=42)

        await proxy.dc_id(5)
        storage.set_session_field.assert_awaited_once_with(42, "dc_id", 5)

    @pytest.mark.asyncio
    async def test_storage_proxy_update_peers(self):
        storage = AsyncMock()
        proxy = BotStorageProxy(storage, bot_id=99)
        peers = [(1, 2, "user", None)]

        await proxy.update_peers(peers)
        storage.update_peers.assert_awaited_once_with(99, peers)

    @pytest.mark.asyncio
    async def test_storage_proxy_update_usernames(self):
        storage = AsyncMock()
        proxy = BotStorageProxy(storage, bot_id=99)
        usernames = [(1, ["alice"])]

        await proxy.update_usernames(usernames)
        storage.update_usernames.assert_awaited_once_with(99, usernames)

    @pytest.mark.asyncio
    async def test_storage_proxy_get_peer_by_id(self):
        storage = AsyncMock()
        storage.get_peer_by_id = AsyncMock(return_value=(1, 2, "user", None))
        proxy = BotStorageProxy(storage, bot_id=10)

        result = await proxy.get_peer_by_id(1)
        storage.get_peer_by_id.assert_awaited_once_with(10, 1)
        assert result == (1, 2, "user", None)

    @pytest.mark.asyncio
    async def test_storage_proxy_delete(self):
        storage = AsyncMock()
        proxy = BotStorageProxy(storage, bot_id=77)

        await proxy.delete()
        storage.delete_session.assert_awaited_once_with(77)

    @pytest.mark.asyncio
    async def test_storage_proxy_open_save_close_are_noops(self):
        storage = AsyncMock()
        proxy = BotStorageProxy(storage, bot_id=1)

        # These should not raise and should not call through to storage
        await proxy.open()
        await proxy.save()
        await proxy.close()

    @pytest.mark.asyncio
    async def test_storage_proxy_all_session_fields(self):
        """Verify every session field getter delegates correctly."""
        storage = AsyncMock()
        storage.get_session_field = AsyncMock(return_value="sentinel")
        proxy = BotStorageProxy(storage, bot_id=5)

        fields = ["api_id", "dc_id", "server_address", "port", "test_mode", "auth_key", "date", "user_id", "is_bot"]
        for field_name in fields:
            storage.get_session_field.reset_mock()
            method = getattr(proxy, field_name)
            result = await method()
            storage.get_session_field.assert_awaited_once_with(5, field_name)
            assert result == "sentinel"

    @pytest.mark.asyncio
    async def test_bot_handle_creates_storage_proxy(self):
        loop = asyncio.get_running_loop()
        runtime = make_runtime(loop)
        bot = BotHandle(runtime, bot_id=42, config=BotConfig(api_id=1), auth_key=b"")

        assert isinstance(bot.storage, BotStorageProxy)
        assert bot.storage._bot_id == 42
        assert bot.storage._storage is runtime.storage
