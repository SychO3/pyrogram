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

from typing import List

from pyrogram import raw, types

from ..object import Object


class BankCardData(Object):
    """Contains information about a bank card.

    Parameters:
        title (``str``):
            Bank card title.

        open_urls (List of :obj:`~pyrogram.types.BankCardOpenUrl`):
            List of URLs with information about the bank card.
    """
    def __init__(
        self,
        *,
        title: str,
        open_urls: List["types.BankCardOpenUrl"]
    ):
        super().__init__()

        self.title = title
        self.open_urls = open_urls

    @staticmethod
    def _parse(data: "raw.types.payments.BankCardData") -> "BankCardData":
        return BankCardData(
            title=data.title,
            open_urls=types.List(
                [types.BankCardOpenUrl._parse(url) for url in data.open_urls]
            )
        )
