"""Tests for MTProto transport frame codecs."""

import struct

import pytest
from binascii import crc32

from pyrogram.connection.transport.codec import (
    AbridgedCodec,
    IntermediateCodec,
    PaddedIntermediateCodec,
    FullCodec,
)


# ---------------------------------------------------------------------------
# AbridgedCodec
# ---------------------------------------------------------------------------

class TestAbridgedCodec:
    def setup_method(self):
        self.codec = AbridgedCodec()

    def test_marker(self):
        assert AbridgedCodec.MARKER == b"\xef"

    def test_encode_small_payload(self):
        """Payload whose length/4 <= 126 uses a 1-byte header."""
        data = b"\x00" * 16  # 16 bytes → length/4 = 4
        encoded = self.codec.encode(data)
        assert encoded[0] == 4
        assert encoded[1:] == data

    def test_encode_large_payload(self):
        """Payload whose length/4 > 126 uses 0x7f + 3-byte LE length."""
        data = b"\xab" * (127 * 4)  # length/4 = 127
        encoded = self.codec.encode(data)
        assert encoded[0] == 0x7F
        assert int.from_bytes(encoded[1:4], "little") == 127
        assert encoded[4:] == data

    def test_encode_request_ack_small(self):
        """request_ack sets the high bit on the 1-byte header."""
        data = b"\x00" * 8  # length/4 = 2
        encoded = self.codec.encode(data, request_ack=True)
        assert encoded[0] == (2 | 0x80)
        assert encoded[1:] == data

    def test_encode_request_ack_large(self):
        """request_ack with large payload uses 0xff as first byte."""
        data = b"\x00" * (127 * 4)
        encoded = self.codec.encode(data, request_ack=True)
        assert encoded[0] == 0xFF
        assert int.from_bytes(encoded[1:4], "little") == 127

    def test_decode_small_frame(self):
        """Round-trip a small payload through encode/decode."""
        data = b"hello world!!!!!"  # 16 bytes
        buf = bytearray(self.codec.encode(data))
        result = self.codec.decode(buf)
        assert result == (data, None)
        assert len(buf) == 0

    def test_decode_large_frame(self):
        """Round-trip a large payload (4-byte header)."""
        data = b"\xcc" * (200 * 4)
        buf = bytearray(self.codec.encode(data))
        result = self.codec.decode(buf)
        assert result == (data, None)
        assert len(buf) == 0

    def test_decode_incremental_small(self):
        """Feeding partial data returns None; feeding the rest succeeds."""
        data = b"\x00" * 20  # 1-byte header + 20 bytes
        encoded = self.codec.encode(data)
        buf = bytearray(encoded[:5])

        assert self.codec.decode(buf) is None  # not enough data
        buf.extend(encoded[5:])
        result = self.codec.decode(buf)
        assert result == (data, None)

    def test_decode_incremental_large(self):
        """Incremental decode with 4-byte header frames."""
        data = b"\x00" * (127 * 4)
        encoded = self.codec.encode(data)
        buf = bytearray(encoded[:2])

        assert self.codec.decode(buf) is None
        buf.extend(encoded[2:])
        result = self.codec.decode(buf)
        assert result == (data, None)

    def test_decode_quick_ack(self):
        """First byte with high bit set is a quick-ack (4 bytes reversed)."""
        token_bytes = bytes([0x82, 0x01, 0x02, 0x03])  # high bit set
        buf = bytearray(token_bytes)
        result = self.codec.decode(buf)
        assert result[0] is None
        assert result[1] == bytes(reversed(token_bytes))
        assert len(buf) == 0

    def test_decode_quick_ack_not_enough_data(self):
        """Quick-ack needs 4 bytes; return None if fewer."""
        buf = bytearray([0x82, 0x01])
        assert self.codec.decode(buf) is None

    def test_decode_empty_buffer(self):
        buf = bytearray()
        assert self.codec.decode(buf) is None


# ---------------------------------------------------------------------------
# IntermediateCodec
# ---------------------------------------------------------------------------

class TestIntermediateCodec:
    def setup_method(self):
        self.codec = IntermediateCodec()

    def test_marker(self):
        assert IntermediateCodec.MARKER == b"\xee\xee\xee\xee"

    def test_encode(self):
        data = b"\xaa" * 32
        encoded = self.codec.encode(data)
        length = struct.unpack("<I", encoded[:4])[0]
        assert length == 32
        assert encoded[4:] == data

    def test_encode_request_ack(self):
        data = b"\xbb" * 16
        encoded = self.codec.encode(data, request_ack=True)
        length = struct.unpack("<I", encoded[:4])[0]
        assert length == (16 | 0x80000000)

    def test_decode_normal(self):
        data = b"test payload !!!"
        buf = bytearray(self.codec.encode(data))
        result = self.codec.decode(buf)
        assert result == (data, None)
        assert len(buf) == 0

    def test_decode_incremental(self):
        data = b"\xff" * 64
        encoded = self.codec.encode(data)
        buf = bytearray(encoded[:10])
        assert self.codec.decode(buf) is None
        buf.extend(encoded[10:])
        result = self.codec.decode(buf)
        assert result == (data, None)

    def test_decode_quick_ack(self):
        """Length with high bit set → quick ack; token is the raw 4 bytes."""
        ack_value = 0x80000001
        buf = bytearray(struct.pack("<I", ack_value))
        result = self.codec.decode(buf)
        assert result[0] is None
        assert result[1] == struct.pack("<I", ack_value)
        assert len(buf) == 0

    def test_decode_empty_buffer(self):
        buf = bytearray()
        assert self.codec.decode(buf) is None


# ---------------------------------------------------------------------------
# PaddedIntermediateCodec
# ---------------------------------------------------------------------------

class TestPaddedIntermediateCodec:
    def setup_method(self):
        self.codec = PaddedIntermediateCodec()

    def test_marker(self):
        assert PaddedIntermediateCodec.MARKER == b"\xdd\xdd\xdd\xdd"

    def test_encode_produces_valid_length_header(self):
        """Encoded frame starts with 4-byte LE length = len(data) + padding."""
        data = b"\x00" * 32
        encoded = self.codec.encode(data)
        total_len = struct.unpack("<I", encoded[:4])[0]
        # total_len is data + padding; padding is 0-15 bytes
        assert 32 <= total_len <= 32 + 15
        assert len(encoded) == 4 + total_len

    def test_decode_strips_padding(self):
        """Manually craft a padded frame and verify decode strips it."""
        payload = b"\xaa" * 32  # 32 bytes, 32 % 16 == 0 → need 8 bytes padding for (tlen-8)%16==0
        padding = b"\x00" * 8  # 8 bytes padding → tlen=40, (40-8)%16=0, payload_len=40
        # Actually: tlen=40, padding_len=(40-8)%16 = 32%16 = 0, payload_len=40
        # That means the whole data section is treated as payload.
        # Let's pick a value where padding is actually stripped:
        # payload=32 bytes, padding=5 bytes → tlen=37, padding_len=(37-8)%16=29%16=13, payload_len=37-13=24
        # Hmm, that strips real data. The protocol assumes payload is always 8 mod 16.
        # So let's use a 24-byte payload (24%16=8 ✓) + 5 padding → tlen=29, (29-8)%16=21%16=5, payload_len=24 ✓
        payload = b"\xaa" * 24
        padding = b"\x00" * 5
        tlen = len(payload) + len(padding)  # 29
        frame = struct.pack("<I", tlen) + payload + padding
        buf = bytearray(frame)
        result = self.codec.decode(buf)
        assert result == (payload, None)
        assert len(buf) == 0

    def test_decode_no_padding(self):
        """When padding is 0 bytes, full data is returned."""
        # payload=40 bytes (40%16=8 ✓), no padding → tlen=40, (40-8)%16=0, payload_len=40
        payload = b"\xbb" * 40
        frame = struct.pack("<I", 40) + payload
        buf = bytearray(frame)
        result = self.codec.decode(buf)
        assert result == (payload, None)

    def test_decode_quick_ack(self):
        """0xFFFFFFFF prefix in data → quick ack with token from next 4 bytes."""
        token = b"\x01\x02\x03\x04"
        ack_data = b"\xff\xff\xff\xff" + token
        tlen = len(ack_data)  # 8
        frame = struct.pack("<I", tlen) + ack_data
        buf = bytearray(frame)
        result = self.codec.decode(buf)
        assert result[0] is None
        assert result[1] == token
        assert len(buf) == 0

    def test_decode_transport_error(self):
        """tlen < 24 (and not a quick ack) → transport error, return first 4 bytes."""
        error_code = b"\x01\x00\x00\x00"
        data = error_code + b"\x00" * 16  # 20 bytes total
        tlen = len(data)  # 20 < 24
        frame = struct.pack("<I", tlen) + data
        buf = bytearray(frame)
        result = self.codec.decode(buf)
        assert result == (error_code, None)
        assert len(buf) == 0

    def test_decode_incremental(self):
        payload = b"\xcc" * 24
        frame = struct.pack("<I", 24) + payload
        buf = bytearray(frame[:6])
        assert self.codec.decode(buf) is None
        buf.extend(frame[6:])
        result = self.codec.decode(buf)
        assert result == (payload, None)

    def test_decode_empty_buffer(self):
        buf = bytearray()
        assert self.codec.decode(buf) is None

    def test_encode_request_ack(self):
        data = b"\x00" * 32
        encoded = self.codec.encode(data, request_ack=True)
        total_len = struct.unpack("<I", encoded[:4])[0]
        assert total_len & 0x80000000  # high bit set


# ---------------------------------------------------------------------------
# FullCodec
# ---------------------------------------------------------------------------

class TestFullCodec:
    def setup_method(self):
        self.codec = FullCodec()

    def test_marker(self):
        assert FullCodec.MARKER is None

    def test_encode_structure(self):
        """Encoded frame: length(4) + seqno(4) + data + CRC32(4)."""
        data = b"hello mtproto!!!"  # 16 bytes
        encoded = self.codec.encode(data)

        total_len = struct.unpack("<I", encoded[:4])[0]
        assert total_len == 16 + 12  # data + length(4) + seqno(4) + crc(4)
        assert len(encoded) == total_len

        seqno = struct.unpack("<I", encoded[4:8])[0]
        assert seqno == 0

        assert encoded[8:-4] == data

        expected_crc = crc32(encoded[:-4])
        actual_crc = struct.unpack("<I", encoded[-4:])[0]
        assert actual_crc == expected_crc

    def test_encode_seqno_increments(self):
        """Each call to encode increments the sequence number."""
        data = b"\x00" * 16
        enc1 = self.codec.encode(data)
        enc2 = self.codec.encode(data)
        enc3 = self.codec.encode(data)

        assert struct.unpack("<I", enc1[4:8])[0] == 0
        assert struct.unpack("<I", enc2[4:8])[0] == 1
        assert struct.unpack("<I", enc3[4:8])[0] == 2

    def test_decode_valid_frame(self):
        """Round-trip encode/decode returns the original payload."""
        data = b"roundtrip test!!"
        buf = bytearray(self.codec.encode(data))
        result = self.codec.decode(buf)
        assert result == (data, None)
        assert len(buf) == 0

    def test_decode_crc_mismatch(self):
        """Corrupted CRC → (None, None), frame is consumed."""
        data = b"\x00" * 16
        encoded = bytearray(self.codec.encode(data))
        # Corrupt the last byte (part of CRC)
        encoded[-1] ^= 0xFF
        buf = bytearray(encoded)
        original_len = len(buf)
        result = self.codec.decode(buf)
        assert result == (None, None)
        assert len(buf) == 0  # frame was consumed

    def test_decode_incremental(self):
        """Partial frame returns None; completing it succeeds."""
        data = b"\xdd" * 32
        encoded = self.codec.encode(data)
        buf = bytearray(encoded[:8])

        assert self.codec.decode(buf) is None
        buf.extend(encoded[8:])
        result = self.codec.decode(buf)
        assert result == (data, None)

    def test_decode_multiple_frames(self):
        """Two frames back-to-back are decoded sequentially."""
        d1 = b"first message!!!"
        d2 = b"second message!!"
        buf = bytearray(self.codec.encode(d1) + self.codec.encode(d2))

        r1 = self.codec.decode(buf)
        assert r1 == (d1, None)

        r2 = self.codec.decode(buf)
        assert r2 == (d2, None)
        assert len(buf) == 0

    def test_decode_invalid_short_length(self):
        """total_len < 12 is invalid → consume 4 bytes, return (None, None)."""
        buf = bytearray(struct.pack("<I", 8))  # length 8 < 12
        result = self.codec.decode(buf)
        assert result == (None, None)
        assert len(buf) == 0

    def test_decode_empty_buffer(self):
        buf = bytearray()
        assert self.codec.decode(buf) is None

    def test_encode_ignores_request_ack(self):
        """Full codec does not support request_ack; flag is silently ignored."""
        data = b"\x00" * 16
        enc_normal = self.codec.encode(data, request_ack=False)
        # Reset seqno for comparison
        self.codec._send_seq_no = 0
        enc_ack = self.codec.encode(data, request_ack=True)
        # Both should be identical since request_ack is unused
        assert enc_normal == enc_ack
