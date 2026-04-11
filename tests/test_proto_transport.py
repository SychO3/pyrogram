"""Tests for asyncio.Protocol-based MTProto transport layer.

Covers MTProtoProtocol (asyncio.Protocol implementation) and
ProtoTransport factory functions.
"""

import asyncio
from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, call

from pyrogram.connection.transport.codec import (
    AbridgedCodec,
    FullCodec,
    IntermediateCodec,
    PaddedIntermediateCodec,
)
from pyrogram.connection.transport.obfuscation import ObfuscationLayer
from pyrogram.connection.transport.proto.mtproto_protocol import (
    HIGH_WATER,
    LOW_WATER,
    MTProtoProtocol,
)
from pyrogram.connection.transport.proto.proto_transport import (
    ProtoAbridged,
    ProtoAbridgedO,
    ProtoFull,
    ProtoIntermediate,
    ProtoIntermediateO,
    ProtoPaddedIntermediateO,
    ProtoTransport,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_protocol(codec=None, obfuscation=None, queue=None, quick_ack_handler=None):
    """Create an MTProtoProtocol with sensible defaults."""
    if codec is None:
        codec = AbridgedCodec()
    if queue is None:
        queue = asyncio.Queue(maxsize=256)
    # Build an ack_source object that holds the handler
    ack_source = None
    if quick_ack_handler is not None:
        ack_source = SimpleNamespace(quick_ack_handler=quick_ack_handler)
    proto = MTProtoProtocol(
        codec=codec,
        obfuscation=obfuscation,
        frame_queue=queue,
        ack_source=ack_source,
    )
    return proto, queue


def _mock_transport():
    """Return a MagicMock mimicking asyncio.Transport."""
    transport = MagicMock(spec=asyncio.Transport)
    transport.is_closing.return_value = False
    return transport


def _abridged_encode(payload: bytes) -> bytes:
    """Encode a payload using the Abridged codec (no obfuscation)."""
    return AbridgedCodec().encode(payload)


# ---------------------------------------------------------------------------
# MTProtoProtocol tests
# ---------------------------------------------------------------------------


class TestMTProtoProtocolConnectionMade:
    """connection_made stores the transport reference."""

    def test_transport_stored(self):
        proto, _ = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)
        assert proto.transport is transport

    def test_transport_initially_none(self):
        proto, _ = _make_protocol()
        assert proto.transport is None


class TestMTProtoProtocolDataReceived:
    """data_received decodes frames and pushes payloads into the queue."""

    def test_single_frame_decoded(self):
        """A complete frame fed in one call should land in the queue."""
        proto, queue = _make_protocol(codec=AbridgedCodec())
        proto.connection_made(_mock_transport())

        payload = b"\x00" * 4  # 4 bytes, abridged length = 1
        encoded = _abridged_encode(payload)
        proto.data_received(encoded)

        assert queue.qsize() == 1
        assert queue.get_nowait() == payload

    def test_multiple_frames_in_one_call(self):
        """Two frames concatenated in a single data_received call."""
        proto, queue = _make_protocol(codec=AbridgedCodec())
        proto.connection_made(_mock_transport())

        p1 = b"\xaa" * 8
        p2 = b"\xbb" * 12
        encoded = _abridged_encode(p1) + _abridged_encode(p2)
        proto.data_received(encoded)

        assert queue.qsize() == 2
        assert queue.get_nowait() == p1
        assert queue.get_nowait() == p2

    def test_incremental_data(self):
        """Partial frame followed by remainder should decode once complete."""
        proto, queue = _make_protocol(codec=AbridgedCodec())
        proto.connection_made(_mock_transport())

        payload = b"\xcc" * 16  # length 4 in abridged units
        encoded = _abridged_encode(payload)

        # Split in the middle
        mid = len(encoded) // 2
        proto.data_received(encoded[:mid])
        assert queue.qsize() == 0  # not yet complete

        proto.data_received(encoded[mid:])
        assert queue.qsize() == 1
        assert queue.get_nowait() == payload

    def test_incremental_single_byte_feeds(self):
        """Feed encoded frame one byte at a time -- should only decode at the end."""
        proto, queue = _make_protocol(codec=AbridgedCodec())
        proto.connection_made(_mock_transport())

        payload = b"\xdd" * 8
        encoded = _abridged_encode(payload)

        for i, byte in enumerate(encoded):
            proto.data_received(bytes([byte]))
            if i < len(encoded) - 1:
                assert queue.qsize() == 0

        assert queue.qsize() == 1
        assert queue.get_nowait() == payload

    def test_intermediate_codec(self):
        """Verify data_received also works with IntermediateCodec."""
        codec = IntermediateCodec()
        proto, queue = _make_protocol(codec=codec)
        proto.connection_made(_mock_transport())

        payload = b"\x42" * 20
        encoded = codec.encode(payload)
        proto.data_received(encoded)

        assert queue.qsize() == 1
        assert queue.get_nowait() == payload

    def test_full_codec(self):
        """Verify data_received works with FullCodec."""
        codec = FullCodec()
        proto, queue = _make_protocol(codec=codec)
        proto.connection_made(_mock_transport())

        payload = b"\x55" * 24
        encoded = codec.encode(payload)
        proto.data_received(encoded)

        assert queue.qsize() == 1
        assert queue.get_nowait() == payload


class TestMTProtoProtocolQuickAck:
    """Quick-ack frames trigger the handler, not the queue."""

    def test_quick_ack_calls_handler(self):
        handler = MagicMock()
        proto, queue = _make_protocol(codec=AbridgedCodec(), quick_ack_handler=handler)
        proto.connection_made(_mock_transport())

        # Abridged quick-ack: first byte has high bit set, total 4 bytes
        ack_data = bytes([0x80, 0x01, 0x02, 0x03])
        proto.data_received(ack_data)

        handler.assert_called_once()
        # The token is the 4 bytes reversed
        expected_token = bytes(reversed(ack_data[:4]))
        handler.assert_called_with(expected_token)
        # Nothing pushed to queue for a quick-ack frame
        assert queue.qsize() == 0

    def test_quick_ack_no_handler(self):
        """If quick_ack_handler is None, ack frames are silently consumed."""
        proto, queue = _make_protocol(codec=AbridgedCodec(), quick_ack_handler=None)
        proto.connection_made(_mock_transport())

        ack_data = bytes([0x80, 0x01, 0x02, 0x03])
        proto.data_received(ack_data)

        assert queue.qsize() == 0  # no crash, no queue entry


class TestMTProtoProtocolObfuscation:
    """data_received decrypts before decoding when obfuscation is set."""

    def test_obfuscated_data_decrypted(self):
        obfuscation = MagicMock(spec=ObfuscationLayer)
        codec = AbridgedCodec()

        payload = b"\x11" * 8
        encoded = codec.encode(payload)
        # decrypt returns the encoded frame -- simulating transparent decrypt
        obfuscation.decrypt.return_value = encoded

        proto, queue = _make_protocol(codec=codec, obfuscation=obfuscation)
        proto.connection_made(_mock_transport())

        # Feed arbitrary bytes (they'll go through the mock decrypt first)
        proto.data_received(b"encrypted_junk_of_same_len")

        obfuscation.decrypt.assert_called_once_with(b"encrypted_junk_of_same_len")
        assert queue.qsize() == 1
        assert queue.get_nowait() == payload


class TestMTProtoProtocolEOF:
    """connection_lost and eof_received push None (EOF sentinel)."""

    def test_connection_lost_sends_eof(self):
        proto, queue = _make_protocol()
        proto.connection_made(_mock_transport())
        proto.connection_lost(None)

        assert queue.qsize() == 1
        assert queue.get_nowait() is None

    def test_connection_lost_with_exception(self):
        proto, queue = _make_protocol()
        proto.connection_made(_mock_transport())
        proto.connection_lost(ConnectionResetError("reset"))

        assert queue.qsize() == 1
        assert queue.get_nowait() is None

    def test_connection_lost_clears_transport(self):
        proto, _ = _make_protocol()
        proto.connection_made(_mock_transport())
        proto.connection_lost(None)
        assert proto.transport is None

    def test_eof_received_sends_eof(self):
        proto, queue = _make_protocol()
        proto.connection_made(_mock_transport())
        result = proto.eof_received()

        assert queue.qsize() == 1
        assert queue.get_nowait() is None
        assert result is False  # do not keep connection half-open


class TestMTProtoProtocolBackpressure:
    """Backpressure: pause at HIGH_WATER, resume at LOW_WATER."""

    def test_pause_reading_at_high_water(self):
        proto, queue = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)

        # Encode HIGH_WATER frames into a single blob and feed them all at once
        payload = b"\x00" * 4
        blob = _abridged_encode(payload) * HIGH_WATER
        proto.data_received(blob)

        assert queue.qsize() == HIGH_WATER
        transport.pause_reading.assert_called_once()

    def test_no_pause_below_high_water(self):
        proto, queue = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)

        payload = b"\x00" * 4
        # Feed one fewer than HIGH_WATER
        blob = _abridged_encode(payload) * (HIGH_WATER - 1)
        proto.data_received(blob)

        assert queue.qsize() == HIGH_WATER - 1
        transport.pause_reading.assert_not_called()

    def test_resume_reading_when_drained(self):
        proto, queue = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)

        # Fill to HIGH_WATER to trigger pause
        payload = b"\x00" * 4
        blob = _abridged_encode(payload) * HIGH_WATER
        proto.data_received(blob)
        assert transport.pause_reading.called

        # Drain until at LOW_WATER
        while queue.qsize() > LOW_WATER:
            queue.get_nowait()

        proto.resume_if_needed()
        transport.resume_reading.assert_called_once()

    def test_resume_not_called_above_low_water(self):
        proto, queue = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)

        # Fill to HIGH_WATER to trigger pause
        payload = b"\x00" * 4
        blob = _abridged_encode(payload) * HIGH_WATER
        proto.data_received(blob)

        # Drain only partially -- still above LOW_WATER
        while queue.qsize() > LOW_WATER + 1:
            queue.get_nowait()

        proto.resume_if_needed()
        transport.resume_reading.assert_not_called()

    def test_resume_idempotent_when_not_paused(self):
        """resume_if_needed is a no-op if reading was never paused."""
        proto, queue = _make_protocol()
        transport = _mock_transport()
        proto.connection_made(transport)

        proto.resume_if_needed()
        transport.resume_reading.assert_not_called()


# ---------------------------------------------------------------------------
# ProtoTransport factory function tests
# ---------------------------------------------------------------------------


class TestProtoTransportFactories:
    """Factory functions produce ProtoTransport with the correct codec/obfuscation."""

    def test_proto_abridged(self):
        t = ProtoAbridged()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, AbridgedCodec)
        assert t._obfuscation is None

    def test_proto_abridged_o(self):
        t = ProtoAbridgedO()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, AbridgedCodec)
        assert isinstance(t._obfuscation, ObfuscationLayer)

    def test_proto_intermediate(self):
        t = ProtoIntermediate()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, IntermediateCodec)
        assert t._obfuscation is None

    def test_proto_intermediate_o(self):
        t = ProtoIntermediateO()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, IntermediateCodec)
        assert isinstance(t._obfuscation, ObfuscationLayer)

    def test_proto_padded_intermediate_o(self):
        t = ProtoPaddedIntermediateO()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, PaddedIntermediateCodec)
        assert isinstance(t._obfuscation, ObfuscationLayer)

    def test_proto_full(self):
        t = ProtoFull()
        assert isinstance(t, ProtoTransport)
        assert isinstance(t._codec, FullCodec)
        assert t._obfuscation is None

    def test_factory_passes_ipv6(self):
        t = ProtoAbridged(ipv6=True)
        assert t.ipv6 is True

    def test_factory_passes_proxy(self):
        proxy = {"scheme": "socks5", "hostname": "127.0.0.1", "port": 1080}
        t = ProtoIntermediate(proxy=proxy)
        assert t.proxy is proxy
