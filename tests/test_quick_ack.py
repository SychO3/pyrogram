import asyncio
import logging

import pytest
from unittest.mock import MagicMock

from pyrogram.session.session import Session


def _make_session():
    """Create a Session with minimal mocked dependencies."""
    client = MagicMock()
    client.loop = asyncio.get_event_loop()

    auth_key = b"\x00" * 256  # 256 bytes, well above the 20-byte sha1 minimum

    session = Session(
        client=client,
        dc_id=2,
        server_address="127.0.0.1",
        port=443,
        auth_key=auth_key,
        test_mode=True,
        is_media=False,
        is_cdn=False,
    )
    return session


class TestQuickAckMethod:
    """Tests for the _on_quick_ack wiring on Session."""

    def test_on_quick_ack_exists(self):
        """Session instances must have a _on_quick_ack method."""
        session = _make_session()
        assert hasattr(session, "_on_quick_ack")

    def test_on_quick_ack_is_callable(self):
        """_on_quick_ack must be callable so it can be used as a handler."""
        session = _make_session()
        assert callable(session._on_quick_ack)

    def test_on_quick_ack_does_not_raise(self):
        """Calling _on_quick_ack with a token should not raise."""
        session = _make_session()
        token = b"\xde\xad\xbe\xef"
        # Should complete without error
        session._on_quick_ack(token)

    def test_on_quick_ack_logs_token(self, caplog):
        """_on_quick_ack should emit a DEBUG log containing the hex token."""
        session = _make_session()
        token = b"\xca\xfe\xba\xbe"

        with caplog.at_level(logging.DEBUG):
            session._on_quick_ack(token)

        # The log message should contain the hex representation of the token
        assert "cafebabe" in caplog.text.lower()

    def test_on_quick_ack_accepts_empty_token(self):
        """_on_quick_ack should handle an empty token gracefully."""
        session = _make_session()
        session._on_quick_ack(b"")
