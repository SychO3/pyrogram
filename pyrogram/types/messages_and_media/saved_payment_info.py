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


class SavedPaymentInfo(Object):
    """Contains information about saved payment information.

    Parameters:
        has_saved_credentials (``bool``):
            True, if the user has saved credentials.

        order_info (:obj:`~pyrogram.types.OrderInfo`, *optional*):
            Saved order information, if any.
    """
    def __init__(
        self,
        *,
        has_saved_credentials: bool,
        order_info: Optional["types.OrderInfo"] = None
    ):
        super().__init__()

        self.has_saved_credentials = has_saved_credentials
        self.order_info = order_info

    @staticmethod
    def _parse(info: "raw.types.payments.SavedInfo") -> "SavedPaymentInfo":
        return SavedPaymentInfo(
            has_saved_credentials=bool(info.has_saved_credentials),
            order_info=types.OrderInfo._parse(info.saved_info)
        )
