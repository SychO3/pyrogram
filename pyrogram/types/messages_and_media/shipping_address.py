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

from pyrogram import raw

from ..object import Object


class ShippingAddress(Object):
    """Contains information about a shipping address.

    Parameters:
        street_line1 (``str``):
            First line for the address.

        street_line2 (``str``):
            Second line for the address.

        city (``str``):
            City.

        state (``str``):
            State, if applicable.

        country_iso2 (``str``):
            Two-letter ISO 3166-1 alpha-2 country code.

        post_code (``str``):
            Address post code.
    """
    def __init__(
        self,
        *,
        street_line1: str,
        street_line2: str,
        city: str,
        state: str,
        country_iso2: str,
        post_code: str
    ):
        super().__init__()

        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.city = city
        self.state = state
        self.country_iso2 = country_iso2
        self.post_code = post_code

    @staticmethod
    def _parse(address: "raw.types.PostAddress") -> "ShippingAddress":
        if address is None:
            return None

        return ShippingAddress(
            street_line1=address.street_line1,
            street_line2=address.street_line2,
            city=address.city,
            state=address.state,
            country_iso2=address.country_iso2,
            post_code=address.post_code
        )

    def write(self):
        return raw.types.PostAddress(
            street_line1=self.street_line1,
            street_line2=self.street_line2,
            city=self.city,
            state=self.state,
            country_iso2=self.country_iso2,
            post_code=self.post_code
        )
