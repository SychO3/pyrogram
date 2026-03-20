import asyncio
import importlib
import struct
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from pyrogram import Client, raw
from pyrogram.errors import SecurityCheckMismatch
from pyrogram.session.session import AuthKeyNotFound, Result, Session


def make_session_client(loop: asyncio.AbstractEventLoop) -> SimpleNamespace:
    return SimpleNamespace(
        loop=loop,
        proxy=None,
        protocol_factory=None,
        connection_factory=None,
        init_connection_params=None,
        storage=SimpleNamespace(api_id=AsyncMock(return_value=1)),
        app_version="Pyrogram Tests",
        device_model="Tests",
        system_version="Tests",
        system_lang_code="en",
        lang_pack="",
        lang_code="en",
        connect_handler=None,
        disconnect_handler=None,
        handle_updates=AsyncMock(),
        _set_server_time=lambda _: None,
        server_time=1.0,
        name="tests",
    )


@pytest.mark.asyncio
async def test_session_send_raises_fatal_error_immediately():
    session = Session(make_session_client(asyncio.get_running_loop()), 1, "127.0.0.1", 443, b"\x01" * 256, False)
    session.fatal_error = AuthKeyNotFound("missing auth key")

    with pytest.raises(AuthKeyNotFound, match="missing auth key"):
        await session.send(raw.functions.Ping(ping_id=0))


@pytest.mark.asyncio
async def test_recv_worker_marks_auth_key_not_found_as_fatal():
    session = Session(make_session_client(asyncio.get_running_loop()), 1, "127.0.0.1", 443, b"\x01" * 256, False)
    pending = Result()
    session.results[1] = pending
    session.is_started.set()
    session.connection = SimpleNamespace(recv=AsyncMock(return_value=struct.pack("<i", -404)))
    session.stop = AsyncMock()

    await session.recv_worker()
    await asyncio.sleep(0)

    assert isinstance(session.fatal_error, AuthKeyNotFound)
    assert pending.value is session.fatal_error
    assert pending.event.is_set()
    session.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_packet_restarts_on_security_check_mismatch(monkeypatch):
    session = Session(make_session_client(asyncio.get_running_loop()), 1, "127.0.0.1", 443, b"\x01" * 256, False)
    session.connection = SimpleNamespace(protocol=SimpleNamespace(crypto_executor=None))
    session.restart = AsyncMock()

    def fail_unpack(*args, **kwargs):
        raise SecurityCheckMismatch("bad packet")

    monkeypatch.setattr("pyrogram.session.session.mtproto.unpack", fail_unpack)

    await session.handle_packet(b"broken")
    await asyncio.sleep(0)

    session.restart.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_session_deduplicates_concurrent_creation(monkeypatch):
    client = Client("test-connection-recovery", api_id=1, api_hash="hash", in_memory=True)
    client.storage = SimpleNamespace(
        dc_id=AsyncMock(return_value=1),
        test_mode=AsyncMock(return_value=False),
        auth_key=AsyncMock(return_value=b"\x01" * 256),
    )
    client.get_dc_option = AsyncMock(return_value=SimpleNamespace(ip_address="127.0.0.1", port=443))

    client_module = importlib.import_module("pyrogram.client")

    class FakeAuth:
        def __init__(self, *args, **kwargs):
            pass

        async def create(self):
            await asyncio.sleep(0.01)
            return b"\x02" * 256

    class FakeSession:
        created = []
        WAIT_TIMEOUT = 1

        def __init__(self, *args, **kwargs):
            self.dc_id = args[1]
            self.is_started = asyncio.Event()
            FakeSession.created.append(self)

        async def start(self):
            await asyncio.sleep(0.01)
            self.is_started.set()

        async def stop(self):
            return None

    monkeypatch.setattr(client_module, "Auth", FakeAuth)
    monkeypatch.setattr(client_module, "Session", FakeSession)

    first, second = await asyncio.gather(
        client.get_session(dc_id=2, export_authorization=False),
        client.get_session(dc_id=2, export_authorization=False),
    )

    assert first is second
    assert len(FakeSession.created) == 1


@pytest.mark.asyncio
async def test_get_session_raises_if_session_never_starts(monkeypatch):
    client = Client("test-connection-start-timeout", api_id=1, api_hash="hash", in_memory=True)
    client.storage = SimpleNamespace(
        dc_id=AsyncMock(return_value=1),
        test_mode=AsyncMock(return_value=False),
        auth_key=AsyncMock(return_value=b"\x01" * 256),
    )
    client.get_dc_option = AsyncMock(return_value=SimpleNamespace(ip_address="127.0.0.1", port=443))

    client_module = importlib.import_module("pyrogram.client")

    class FakeAuth:
        def __init__(self, *args, **kwargs):
            pass

        async def create(self):
            return b"\x02" * 256

    class FakeSession:
        def __init__(self, *args, **kwargs):
            self.is_started = asyncio.Event()
            self.stop = AsyncMock()

        async def start(self):
            return None

    monkeypatch.setattr(client_module, "Auth", FakeAuth)
    monkeypatch.setattr(client_module, "Session", FakeSession)
    monkeypatch.setattr(client_module.Session, "WAIT_TIMEOUT", 0.01, raising=False)

    with pytest.raises(ConnectionError, match="Failed to start session for DC2"):
        await client.get_session(dc_id=2, export_authorization=False)
