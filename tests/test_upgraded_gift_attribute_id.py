#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from pyrogram import raw, types
from pyrogram.types.messages_and_media.upgraded_gift_attribute_id import UpgradedGiftAttributeId


def test_parse_none():
    result = UpgradedGiftAttributeId._parse(None)
    assert result is None


def test_parse_model():
    attr = raw.types.StarGiftAttributeIdModel(document_id=12345)
    result = UpgradedGiftAttributeId._parse(attr)
    assert isinstance(result, types.UpgradedGiftAttributeIdModel)
    assert result.sticker_id == 12345


def test_parse_pattern():
    attr = raw.types.StarGiftAttributeIdPattern(document_id=67890)
    result = UpgradedGiftAttributeId._parse(attr)
    assert isinstance(result, types.UpgradedGiftAttributeIdSymbol)
    assert result.sticker_id == 67890


def test_parse_backdrop():
    attr = raw.types.StarGiftAttributeIdBackdrop(backdrop_id=11111)
    result = UpgradedGiftAttributeId._parse(attr)
    assert isinstance(result, types.UpgradedGiftAttributeIdBackdrop)
    assert result.backdrop_id == 11111
