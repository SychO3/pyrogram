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
SentMessage: semantic subtype for the prompt message sent by ask().

This class inherits from the core :class:`~pyrogram.types.Message`, so it
exposes the full Message API (e.g., delete, edit, reply) while providing a
stable name to reference the prompt message in type hints and docs.
"""

from pyrogram.types.messages_and_media.message import Message as _Message


class SentMessage(_Message):
    pass


__all__ = ["SentMessage"]


