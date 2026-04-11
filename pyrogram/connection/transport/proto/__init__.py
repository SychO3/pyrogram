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

"""asyncio.Protocol-based MTProto transports.

Push-model transport that uses asyncio.Protocol instead of StreamReader/Writer.
Frames are pushed into an asyncio.Queue for pull-style consumption by Session.
"""

from .proto_transport import (
    ProtoAbridged,
    ProtoAbridgedO,
    ProtoFull,
    ProtoIntermediate,
    ProtoIntermediateO,
    ProtoPaddedIntermediateO,
    ProtoTransport,
)
from .mtproto_protocol import MTProtoProtocol

__all__ = [
    "MTProtoProtocol",
    "ProtoTransport",
    "ProtoAbridged",
    "ProtoAbridgedO",
    "ProtoIntermediate",
    "ProtoIntermediateO",
    "ProtoPaddedIntermediateO",
    "ProtoFull",
]
