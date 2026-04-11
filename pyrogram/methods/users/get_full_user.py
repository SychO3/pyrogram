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

from typing import Union

import pyrogram
from pyrogram import raw
from pyrogram import types


class GetFullUser:
    async def get_full_user(
        self: "pyrogram.Client",
        user_id: Union[int, str]
    ) -> "types.User":
        """Get full information about a user.

        This method returns a user with all available fields populated, including
        bio, birthday, registration_month, settings, and other fields that are only
        available through the full user API.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            :obj:`~pyrogram.types.User`: Full information about the user.

        Example:
            .. code-block:: python

                user = await app.get_full_user(user_id)
                print(user.bio)
                print(user.registration_month)
        """
        peer = await self.resolve_peer(user_id)

        r = await self.invoke(
            raw.functions.users.GetFullUser(
                id=peer
            )
        )

        users = {u.id: u for u in r.users}
        chats = {c.id: c for c in r.chats}

        return await types.User._parse_full(self, r.full_user, users, chats)
