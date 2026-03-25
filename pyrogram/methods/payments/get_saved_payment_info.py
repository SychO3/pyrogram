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
from pyrogram import raw, types


class GetSavedPaymentInfo:
    async def get_saved_payment_info(
        self: "pyrogram.Client",
    ) -> "types.SavedPaymentInfo":
        """Get saved payment information.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.types.SavedPaymentInfo`: On success, the saved payment info is returned.

        Example:
            .. code-block:: python

                info = await app.get_saved_payment_info()

                if info.has_saved_credentials:
                    print("Has saved credentials")

                if info.order_info:
                    print(info.order_info.name)
        """
        r = await self.invoke(
            raw.functions.payments.GetSavedInfo()
        )

        return types.SavedPaymentInfo._parse(r)
