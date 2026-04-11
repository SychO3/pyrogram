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


class SavePreparedKeyboardButton:
    async def save_prepared_keyboard_button(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        button: "types.KeyboardButton",
    ) -> "types.PreparedKeyboardButton":
        """Save a keyboard button to be used later in a Mini App.

        This allows bots to request users, chats and managed bots from Mini Apps.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user
                that will use this button in the Mini App.

            button (:obj:`~pyrogram.types.KeyboardButton`):
                The keyboard button to save.

        Returns:
            :obj:`~pyrogram.types.PreparedKeyboardButton`: On success, the prepared keyboard button is returned.
        """
        r = await self.invoke(
            raw.functions.bots.RequestWebViewButton(
                user_id=await self.resolve_peer(user_id),
                button=button.write()
            )
        )

        return types.PreparedKeyboardButton._parse(r)
