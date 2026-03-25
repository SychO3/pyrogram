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

import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class PaymentReceipt(Object):
    """Contains information about a payment receipt.

    Parameters:
        date (:py:obj:`~datetime.datetime`):
            Date the payment was made.

        bot_id (``int``):
            User identifier of the seller bot.

        bot (:obj:`~pyrogram.types.User`, *optional*):
            Information about the seller bot.

        provider_id (``int``):
            User identifier of the payment provider.

        title (``str``):
            Product name.

        description (``str``):
            Product description.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Product photo.

        invoice (:obj:`~pyrogram.types.Invoice`, *optional*):
            Full information about the invoice.

        currency (``str``):
            Three-letter ISO 4217 currency code.

        total_amount (``int``):
            Total price in the smallest units of the currency.

        credentials_title (``str``):
            Title of the saved credentials chosen by the buyer.

        order_info (:obj:`~pyrogram.types.OrderInfo`, *optional*):
            Information about the buyer.

        shipping (:obj:`~pyrogram.types.ShippingOption`, *optional*):
            Shipping option chosen by the user.

        tip_amount (``int``, *optional*):
            The amount of tip in the smallest units of the currency.

        raw (:obj:`~pyrogram.raw.base.payments.PaymentReceipt`, *optional*):
            The raw object, as received from the Telegram API.
    """
    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        date: datetime.datetime,
        bot_id: int,
        bot: Optional["types.User"] = None,
        provider_id: int,
        title: str,
        description: str,
        photo: Optional["types.Photo"] = None,
        invoice: Optional["types.Invoice"] = None,
        currency: str,
        total_amount: int,
        credentials_title: str,
        order_info: Optional["types.OrderInfo"] = None,
        shipping: Optional["types.ShippingOption"] = None,
        tip_amount: Optional[int] = None,
        raw: "raw.base.payments.PaymentReceipt" = None,
    ):
        super().__init__(client)

        self.date = date
        self.bot_id = bot_id
        self.bot = bot
        self.provider_id = provider_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.currency = currency
        self.total_amount = total_amount
        self.credentials_title = credentials_title
        self.order_info = order_info
        self.shipping = shipping
        self.tip_amount = tip_amount
        self.raw = raw

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        receipt: "raw.base.payments.PaymentReceipt"
    ) -> "PaymentReceipt":
        users = {i.id: i for i in getattr(receipt, "users", [])}

        if isinstance(receipt, raw.types.payments.PaymentReceipt):
            return PaymentReceipt(
                client=client,
                date=utils.timestamp_to_datetime(receipt.date),
                bot_id=receipt.bot_id,
                bot=types.User._parse(client, users.get(receipt.bot_id)),
                provider_id=receipt.provider_id,
                title=receipt.title,
                description=receipt.description,
                photo=types.Photo._parse(client, receipt.photo),
                invoice=types.Invoice._parse(client, receipt.invoice),
                currency=receipt.currency,
                total_amount=receipt.total_amount,
                credentials_title=receipt.credentials_title,
                order_info=types.OrderInfo._parse(receipt.info),
                shipping=types.ShippingOption._parse(receipt.shipping) if receipt.shipping else None,
                tip_amount=receipt.tip_amount,
                raw=receipt
            )

        if isinstance(receipt, raw.types.payments.PaymentReceiptStars):
            return PaymentReceipt(
                client=client,
                date=utils.timestamp_to_datetime(receipt.date),
                bot_id=receipt.bot_id,
                bot=types.User._parse(client, users.get(receipt.bot_id)),
                provider_id=0,
                title=receipt.title,
                description=receipt.description,
                photo=types.Photo._parse(client, receipt.photo),
                invoice=types.Invoice._parse(client, receipt.invoice),
                currency=receipt.currency,
                total_amount=receipt.total_amount,
                credentials_title="",
                raw=receipt
            )
