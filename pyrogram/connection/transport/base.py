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

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Tuple


class TransportBase(ABC):
    """Abstract base class for MTProto transport protocols.

    All transports (TCP pull-based, asyncio.Protocol push-based, WebSocket)
    implement this interface so that Connection and Session can use them
    interchangeably.
    """

    crypto_executor: Any = None
    quick_ack_handler: Optional[Callable[[bytes], None]] = None

    @abstractmethod
    async def connect(self, address: Tuple[str, int]) -> None:
        ...

    @abstractmethod
    async def send(self, data: bytes, request_ack: bool = False) -> None:
        ...

    @abstractmethod
    async def recv(self) -> Optional[bytes]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
