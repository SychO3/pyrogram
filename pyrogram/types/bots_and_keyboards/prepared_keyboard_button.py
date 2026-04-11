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


class PreparedKeyboardButton(Object):
    """Describes a keyboard button that was saved by the bot for use in a Web App.

    Parameters:
        id (``str``):
            Unique identifier of the prepared button.
    """

    def __init__(self, *, id: str):
        super().__init__()

        self.id = id

    @staticmethod
    def _parse(obj: "raw.types.bots.RequestedButton") -> "PreparedKeyboardButton":
        return PreparedKeyboardButton(id=obj.webapp_req_id)
