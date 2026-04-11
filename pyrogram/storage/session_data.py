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

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SessionData:
    bot_id: int
    dc_id: int = 2
    server_address: str = "149.154.167.51"
    port: int = 443
    api_id: Optional[int] = None
    test_mode: bool = False
    auth_key: Optional[bytes] = None
    date: int = 0
    user_id: Optional[int] = None
    is_bot: Optional[bool] = None
