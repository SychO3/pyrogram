"""Tests for the MTProto obfuscation layer (AES-256-CTR)."""

import pytest

from pyrogram.connection.transport.obfuscation import ObfuscationLayer, RESERVED


MARKER_ABRIDGED = b"\xef\xef\xef\xef"
MARKER_INTERMEDIATE = b"\xee\xee\xee\xee"


# ---------------------------------------------------------------------------
# Nonce generation
# ---------------------------------------------------------------------------

def test_nonce_length():
    """generate_nonce() returns exactly 64 bytes."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    nonce = layer.generate_nonce()
    assert len(nonce) == 64


def test_nonce_first_byte_not_ef():
    """First byte of the nonce must not be 0xef."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    for _ in range(50):
        nonce = layer.generate_nonce()
        assert nonce[0] != 0xEF


def test_nonce_first_four_bytes_not_reserved():
    """First 4 bytes of the nonce must not match any RESERVED prefix."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    for _ in range(50):
        nonce = layer.generate_nonce()
        assert nonce[:4] not in RESERVED


def test_nonce_bytes_4_to_8_not_zero():
    """Bytes 4-8 of the nonce must not be all zeros."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    for _ in range(50):
        nonce = layer.generate_nonce()
        assert nonce[4:8] != b"\x00" * 4


# ---------------------------------------------------------------------------
# Protocol marker embedding (indirect check)
# ---------------------------------------------------------------------------

def test_nonce_is_bytes_and_correct_length():
    """Nonce is returned as bytes with the correct length, confirming the
    marker-embedding path was reached (bytes 56:64 are encrypted so we
    cannot directly inspect the plaintext marker)."""
    layer = ObfuscationLayer(MARKER_INTERMEDIATE)
    nonce = layer.generate_nonce()
    assert isinstance(nonce, bytes)
    assert len(nonce) == 64


# ---------------------------------------------------------------------------
# Encrypt / decrypt roundtrip
# ---------------------------------------------------------------------------

def test_encrypt_produces_different_output():
    """Encrypted data must differ from the plaintext."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    layer.generate_nonce()
    plaintext = b"hello world, this is a test message!"
    ciphertext = layer.encrypt(plaintext)
    assert ciphertext != plaintext
    assert len(ciphertext) == len(plaintext)


def test_roundtrip_with_swapped_keys():
    """Encrypt with one layer, decrypt with a separate layer that shares
    the same key/iv/state snapshot.  AES-CTR state advances on each call,
    so we snapshot the encrypt state right after generate_nonce() and
    assign the copy to a second layer's decrypt side."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    layer.generate_nonce()

    # Snapshot the encrypt key material (iv and state are mutable bytearrays
    # that will be mutated by encrypt(), so we must copy them now).
    enc_key = layer._encrypt[0]
    enc_iv = bytearray(layer._encrypt[1])
    enc_state = bytearray(layer._encrypt[2])

    plaintext = b"A" * 64
    ciphertext = layer.encrypt(plaintext)

    # Build a decryptor with the same key/iv/state starting point
    dec = ObfuscationLayer(MARKER_ABRIDGED)
    dec._decrypt = (enc_key, enc_iv, enc_state)
    recovered = dec.decrypt(ciphertext)
    assert recovered == plaintext


# ---------------------------------------------------------------------------
# CTR state advances
# ---------------------------------------------------------------------------

def test_ctr_state_advances():
    """Encrypting the same plaintext twice produces different ciphertext
    because the AES-CTR counter advances."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    layer.generate_nonce()

    data = b"same data every time"
    ct1 = layer.encrypt(data)
    ct2 = layer.encrypt(data)
    assert ct1 != ct2


def test_multiple_chunks_cumulative():
    """Encrypting data in two chunks is equivalent to the CTR state
    advancing across both calls — the second chunk's ciphertext depends
    on the first."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    layer.generate_nonce()

    chunk1 = b"A" * 16
    chunk2 = b"B" * 16

    ct_chunk1 = layer.encrypt(chunk1)
    ct_chunk2 = layer.encrypt(chunk2)

    # Both must be 16 bytes and differ from plaintext
    assert len(ct_chunk1) == 16
    assert len(ct_chunk2) == 16
    assert ct_chunk1 != chunk1
    assert ct_chunk2 != chunk2

    # The two ciphertexts must differ from each other (different plaintext
    # at different CTR offsets)
    assert ct_chunk1 != ct_chunk2


# ---------------------------------------------------------------------------
# Error handling: encrypt/decrypt before generate_nonce
# ---------------------------------------------------------------------------

def test_encrypt_before_nonce_raises():
    """Calling encrypt() before generate_nonce() must raise RuntimeError."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    with pytest.raises(RuntimeError, match="generate_nonce"):
        layer.encrypt(b"data")


def test_decrypt_before_nonce_raises():
    """Calling decrypt() before generate_nonce() must raise RuntimeError."""
    layer = ObfuscationLayer(MARKER_ABRIDGED)
    with pytest.raises(RuntimeError, match="generate_nonce"):
        layer.decrypt(b"data")


# ---------------------------------------------------------------------------
# Invalid marker length
# ---------------------------------------------------------------------------

def test_marker_too_short_raises():
    """A 3-byte marker must raise ValueError."""
    with pytest.raises(ValueError, match="4 bytes"):
        ObfuscationLayer(b"\xef\xef\xef")


def test_marker_too_long_raises():
    """A 5-byte marker must raise ValueError."""
    with pytest.raises(ValueError, match="4 bytes"):
        ObfuscationLayer(b"\xef\xef\xef\xef\xef")
