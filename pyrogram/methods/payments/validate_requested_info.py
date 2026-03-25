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
from pyrogram import raw, types


class ValidateRequestedInfo:
    async def validate_requested_info(
        self: "pyrogram.Client",
        input_invoice: "types.InputInvoice",
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        shipping_address: Optional["types.ShippingAddress"] = None,
        save: Optional[bool] = None
    ) -> "types.ValidatedOrderInfo":
        """Validate order information provided by the user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            input_invoice (:obj:`~pyrogram.types.InputInvoice`):
                The invoice.

            name (``str``, *optional*):
                User's full name.

            phone (``str``, *optional*):
                User's phone number.

            email (``str``, *optional*):
                User's email address.

            shipping_address (:obj:`~pyrogram.types.ShippingAddress`, *optional*):
                User's shipping address.

            save (``bool``, *optional*):
                Pass True to save the order information for future use.

        Returns:
            :obj:`~pyrogram.types.ValidatedOrderInfo`: On success, the validated order info is returned.

        Example:
            .. code-block:: python

                invoice = types.InputInvoiceMessage(
                    chat_id=chat_id,
                    message_id=123
                )

                validated = await app.validate_requested_info(
                    input_invoice=invoice,
                    name="John Doe",
                    email="john@example.com",
                    shipping_address=types.ShippingAddress(
                        street_line1="123 Main St",
                        street_line2="",
                        city="New York",
                        state="NY",
                        country_iso2="US",
                        post_code="10001"
                    ),
                    save=True
                )
        """
        r = await self.invoke(
            raw.functions.payments.ValidateRequestedInfo(
                invoice=await input_invoice.write(self),
                info=raw.types.PaymentRequestedInfo(
                    name=name,
                    phone=phone,
                    email=email,
                    shipping_address=shipping_address.write() if shipping_address else None
                ),
                save=save
            )
        )

        return types.ValidatedOrderInfo._parse(r)
