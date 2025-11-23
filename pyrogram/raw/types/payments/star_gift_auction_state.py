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

from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Any

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject

if TYPE_CHECKING:
    from pyrogram import raw

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class StarGiftAuctionState(TLObject):
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.payments.StarGiftAuctionState`.

    Details:
        - Layer: ``218``
        - ID: ``E98E474``

    Parameters:
        gift: :obj:`StarGift <pyrogram.raw.base.StarGift>`
        state: :obj:`StarGiftAuctionState <pyrogram.raw.base.StarGiftAuctionState>`
        user_state: :obj:`StarGiftAuctionUserState <pyrogram.raw.base.StarGiftAuctionUserState>`
        timeout: ``int`` ``32-bit``
        users: List of :obj:`User <pyrogram.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetStarGiftAuctionState <pyrogram.raw.functions.payments.GetStarGiftAuctionState>`
    """

    __slots__: List[str] = ["gift", "state", "user_state", "timeout", "users"]

    ID = 0xe98e474
    QUALNAME = "types.payments.StarGiftAuctionState"

    def __init__(self, *, gift: "raw.base.StarGift", state: "raw.base.StarGiftAuctionState", user_state: "raw.base.StarGiftAuctionUserState", timeout: int, users: List["raw.base.User"]) -> None:
        self.gift = gift  # StarGift
        self.state = state  # StarGiftAuctionState
        self.user_state = user_state  # StarGiftAuctionUserState
        self.timeout = timeout  # int
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGiftAuctionState":
        # No flags
        
        gift = TLObject.read(b)
        
        state = TLObject.read(b)
        
        user_state = TLObject.read(b)
        
        timeout = Int.read(b)
        
        users = TLObject.read(b)
        
        return StarGiftAuctionState(gift=gift, state=state, user_state=user_state, timeout=timeout, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.gift.write())
        
        b.write(self.state.write())
        
        b.write(self.user_state.write())
        
        b.write(Int(self.timeout))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
