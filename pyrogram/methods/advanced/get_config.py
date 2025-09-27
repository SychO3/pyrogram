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

import pyrogram
from pyrogram import raw


class GetConfig:
    async def get_config(self: "pyrogram.Client") -> "raw.types.Config":
        """Fetch Telegram configuration (dc options, limits, etc.).

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            :obj:`pyrogram.raw.types.Config`: The raw Telegram configuration object.
        """
        if not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        return await self.invoke(raw.functions.help.GetConfig())


