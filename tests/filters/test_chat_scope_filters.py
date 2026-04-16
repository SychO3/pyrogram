import pytest

from pyrogram import filters
from pyrogram.types import ManagedBotUpdated
from tests.filters import Client


@pytest.mark.asyncio
async def test_private_filter_update_without_chat_returns_false():
    c = Client()
    update = ManagedBotUpdated(user=None, bot=None)

    assert not await filters.private(c, update)
