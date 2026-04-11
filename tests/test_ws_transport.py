"""Tests for pyrogram.connection.transport.ws.ws_transport."""

import asyncio
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pyrogram.connection.transport.codec import (
    AbridgedCodec,
    IntermediateCodec,
    PaddedIntermediateCodec,
)
from pyrogram.connection.transport.obfuscation import ObfuscationLayer
from pyrogram.connection.transport.ws.ws_transport import (
    WSTransport,
    WSAbridgedO,
    WSIntermediateO,
    WSPaddedIntermediateO,
)


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------


class TestWSAbridgedOFactory:
    def test_creates_ws_transport_instance(self):
        t = WSAbridgedO()
        assert isinstance(t, WSTransport)

    def test_uses_abridged_codec(self):
        t = WSAbridgedO()
        assert isinstance(t._codec, AbridgedCodec)

    def test_uses_obfuscation_with_ef_marker(self):
        t = WSAbridgedO()
        assert isinstance(t._obfuscation, ObfuscationLayer)
        assert t._obfuscation._marker == b"\xef\xef\xef\xef"


class TestWSIntermediateOFactory:
    def test_creates_ws_transport_instance(self):
        t = WSIntermediateO()
        assert isinstance(t, WSTransport)

    def test_uses_intermediate_codec(self):
        t = WSIntermediateO()
        assert isinstance(t._codec, IntermediateCodec)

    def test_uses_obfuscation_with_ee_marker(self):
        t = WSIntermediateO()
        assert isinstance(t._obfuscation, ObfuscationLayer)
        assert t._obfuscation._marker == b"\xee\xee\xee\xee"


class TestWSPaddedIntermediateOFactory:
    def test_creates_ws_transport_instance(self):
        t = WSPaddedIntermediateO()
        assert isinstance(t, WSTransport)

    def test_uses_padded_intermediate_codec(self):
        t = WSPaddedIntermediateO()
        assert isinstance(t._codec, PaddedIntermediateCodec)

    def test_uses_obfuscation_with_dd_marker(self):
        t = WSPaddedIntermediateO()
        assert isinstance(t._obfuscation, ObfuscationLayer)
        assert t._obfuscation._marker == b"\xdd\xdd\xdd\xdd"


# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------


class TestWSTransportConstructor:
    def test_default_state_is_disconnected(self):
        t = WSAbridgedO()
        assert t._ws is None
        assert t._session is None
        assert t._recv_task is None

    def test_queue_created_with_capacity(self):
        t = WSAbridgedO()
        assert isinstance(t._queue, asyncio.Queue)
        assert t._queue.maxsize == 256

    def test_ipv6_and_proxy_forwarded(self):
        t = WSAbridgedO(ipv6=True, proxy={"scheme": "socks5", "hostname": "localhost"})
        assert t.ipv6 is True
        assert t.proxy == {"scheme": "socks5", "hostname": "localhost"}

    def test_custom_crypto_executor(self):
        from concurrent.futures import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=2)
        try:
            t = WSAbridgedO(crypto_executor=executor)
            assert t.crypto_executor is executor
            assert t._owns_crypto_executor is False
        finally:
            executor.shutdown(wait=False)

    def test_default_crypto_executor_is_owned(self):
        t = WSAbridgedO()
        assert t._owns_crypto_executor is True
        t.crypto_executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# send — requires open connection
# ---------------------------------------------------------------------------


class TestSendWhenClosed:
    @pytest.mark.asyncio
    async def test_send_raises_oserror_when_ws_is_none(self):
        t = WSAbridgedO()
        assert t._ws is None
        with pytest.raises(OSError, match="closed"):
            await t.send(b"\x00" * 16)

    @pytest.mark.asyncio
    async def test_send_raises_oserror_when_ws_is_closed(self):
        t = WSAbridgedO()
        mock_ws = MagicMock()
        mock_ws.closed = True
        t._ws = mock_ws
        with pytest.raises(OSError, match="closed"):
            await t.send(b"\x00" * 16)


# ---------------------------------------------------------------------------
# recv — queue semantics
# ---------------------------------------------------------------------------


class TestRecvFromQueue:
    @pytest.mark.asyncio
    async def test_recv_returns_frame_from_queue(self):
        t = WSAbridgedO()
        payload = b"test-payload-data"
        t._queue.put_nowait(payload)
        result = await t.recv()
        assert result == payload

    @pytest.mark.asyncio
    async def test_recv_returns_none_sentinel(self):
        """A None in the queue signals EOF from the recv loop."""
        t = WSAbridgedO()
        t._queue.put_nowait(None)
        result = await t.recv()
        assert result is None

    @pytest.mark.asyncio
    async def test_recv_preserves_fifo_order(self):
        t = WSAbridgedO()
        frames = [b"first", b"second", b"third"]
        for f in frames:
            t._queue.put_nowait(f)
        for expected in frames:
            assert await t.recv() == expected


# ---------------------------------------------------------------------------
# close — idempotent
# ---------------------------------------------------------------------------


class TestCloseIdempotent:
    @pytest.mark.asyncio
    async def test_close_on_fresh_transport_does_not_raise(self):
        t = WSAbridgedO()
        await t.close()  # should not raise

    @pytest.mark.asyncio
    async def test_close_twice_does_not_raise(self):
        t = WSAbridgedO()
        await t.close()
        await t.close()  # second call should be a no-op

    @pytest.mark.asyncio
    async def test_close_cancels_recv_task(self):
        t = WSAbridgedO()

        async def long_running():
            await asyncio.sleep(3600)

        task = asyncio.ensure_future(long_running())
        t._recv_task = task

        await t.close()
        assert task.cancelled()
        assert t._recv_task is None

    @pytest.mark.asyncio
    async def test_close_closes_ws_and_session(self):
        t = WSAbridgedO()

        mock_ws = AsyncMock()
        mock_ws.closed = False
        t._ws = mock_ws

        mock_session = AsyncMock()
        mock_session.closed = False
        t._session = mock_session

        await t.close()

        mock_ws.close.assert_awaited_once()
        mock_session.close.assert_awaited_once()
        assert t._ws is None
        assert t._session is None

    @pytest.mark.asyncio
    async def test_close_shuts_down_owned_executor(self):
        t = WSAbridgedO()
        assert t._owns_crypto_executor is True
        executor = MagicMock()
        t.crypto_executor = executor

        await t.close()
        executor.shutdown.assert_called_once_with(wait=False)
