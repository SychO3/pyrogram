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

"""
Lightweight structures representing the prompt returned by ask().

These dataclasses reflect the minimal, stable shape of the object attached to
`sent_message` in the ask() response, independent from the full
`pyrogram.types.Message` model.
"""

from dataclasses import dataclass
from typing import Optional
from pyrogram.types.messages_and_media.message import Str as _TextStr
from pyrogram.enums import ChatType as _ChatType


@dataclass
class SentChat:
    _ : str
    id: int
    type: _ChatType


@dataclass
class SentMessage:
    _ : str
    id: int
    date: str
    chat: SentChat
    text: Optional[_TextStr]
    outgoing: bool


__all__ = ["SentMessage", "SentChat"]


