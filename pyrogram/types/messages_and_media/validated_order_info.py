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

from typing import List, Optional

from pyrogram import raw, types

from ..object import Object


class ValidatedOrderInfo(Object):
    """Contains the result of a validated order information request.

    Parameters:
        id (``str``, *optional*):
            Temporary identifier for the validated order information.
            Pass this to :meth:`~pyrogram.Client.send_payment_form` as ``requested_info_id``.

        shipping_options (List of :obj:`~pyrogram.types.ShippingOption`, *optional*):
            Available shipping options, if any.
    """
    def __init__(
        self,
        *,
        id: Optional[str] = None,
        shipping_options: Optional[List["types.ShippingOption"]] = None
    ):
        super().__init__()

        self.id = id
        self.shipping_options = shipping_options

    @staticmethod
    def _parse(info: "raw.types.payments.ValidatedRequestedInfo") -> "ValidatedOrderInfo":
        return ValidatedOrderInfo(
            id=info.id,
            shipping_options=types.List(
                [types.ShippingOption._parse(opt) for opt in info.shipping_options]
            ) if info.shipping_options else None
        )
