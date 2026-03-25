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

from pyrogram import raw, types

from ..object import Object


class OrderInfo(Object):
    """Contains information about the buyer in a payment process.

    Parameters:
        name (``str``, *optional*):
            User's full name.

        phone (``str``, *optional*):
            User's phone number.

        email (``str``, *optional*):
            User's email address.

        shipping_address (:obj:`~pyrogram.types.ShippingAddress`, *optional*):
            User's shipping address.
    """
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        shipping_address: Optional["types.ShippingAddress"] = None
    ):
        super().__init__()

        self.name = name
        self.phone = phone
        self.email = email
        self.shipping_address = shipping_address

    @staticmethod
    def _parse(info: "raw.types.PaymentRequestedInfo") -> "OrderInfo":
        if info is None:
            return None

        return OrderInfo(
            name=info.name,
            phone=info.phone,
            email=info.email,
            shipping_address=types.ShippingAddress._parse(info.shipping_address)
        )

    def write(self):
        return raw.types.PaymentRequestedInfo(
            name=self.name,
            phone=self.phone,
            email=self.email,
            shipping_address=self.shipping_address.write() if self.shipping_address else None
        )
