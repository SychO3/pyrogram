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
from pyrogram import raw, types


class GetUserProfileAudios:
    async def get_user_profile_audios(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        offset: int = 0,
        limit: int = 100
    ) -> "types.UserProfileAudios":
        """Get a user's profile audios.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            offset (``int``, *optional*):
                Sequential number of the first audio to be returned.
                Defaults to 0.

            limit (``int``, *optional*):
                Limits the number of audios to be retrieved.
                Values between 1-100 are accepted. Defaults to 100.

        Returns:
            :obj:`~pyrogram.types.UserProfileAudios`: On success, a UserProfileAudios object is returned.

        Example:
            .. code-block:: python

                audios = await app.get_user_profile_audios("me")
                print(audios.total_count)
        """
        peer_id = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.users.GetSavedMusic(
                id=peer_id,
                offset=offset,
                limit=limit,
                hash=0
            )
        )

        return types.UserProfileAudios._parse(self, r)
