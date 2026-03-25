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

from typing import Optional

import pyrogram
from pyrogram import raw


class ClearSavedPaymentInfo:
    async def clear_saved_payment_info(
        self: "pyrogram.Client",
        credentials: Optional[bool] = None,
        info: Optional[bool] = None
    ) -> bool:
        """Clear saved payment information.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            credentials (``bool``, *optional*):
                Pass True to remove saved payment credentials.

            info (``bool``, *optional*):
                Pass True to remove saved order information.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Clear both credentials and info
                await app.clear_saved_payment_info(
                    credentials=True,
                    info=True
                )

                # Clear only saved credentials
                await app.clear_saved_payment_info(credentials=True)
        """
        r = await self.invoke(
            raw.functions.payments.ClearSavedInfo(
                credentials=credentials,
                info=info
            )
        )

        return bool(r)
