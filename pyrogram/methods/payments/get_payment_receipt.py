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


class GetPaymentReceipt:
    async def get_payment_receipt(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int
    ) -> "types.PaymentReceipt":
        """Get a payment receipt.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message with the successful payment service message.

        Returns:
            :obj:`~pyrogram.types.PaymentReceipt`: On success, the payment receipt is returned.

        Example:
            .. code-block:: python

                receipt = await app.get_payment_receipt(
                    chat_id=chat_id,
                    message_id=123
                )

                print(receipt.total_amount, receipt.currency)
        """
        r = await self.invoke(
            raw.functions.payments.GetPaymentReceipt(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id
            )
        )

        return types.PaymentReceipt._parse(self, r)
