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


class GetBankCardData:
    async def get_bank_card_data(
        self: "pyrogram.Client",
        number: str
    ) -> "types.BankCardData":
        """Get information about a bank card by its number.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            number (``str``):
                The bank card number.

        Returns:
            :obj:`~pyrogram.types.BankCardData`: On success, the bank card data is returned.

        Example:
            .. code-block:: python

                data = await app.get_bank_card_data("1234567890123456")

                print(data.title)
                for link in data.open_urls:
                    print(link.name, link.url)
        """
        r = await self.invoke(
            raw.functions.payments.GetBankCardData(
                number=number
            )
        )

        return types.BankCardData._parse(r)
