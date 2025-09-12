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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

# We need to dynamically set `__doc__` due to `sphinx`
AffectedHistory = Union[raw.types.messages.AffectedHistory]
AffectedHistory.__doc__ = """
    This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AffectedHistory <pyrogram.raw.types.messages.AffectedHistory>`

    See Also:
        This object can be returned by 7 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeleteHistory <pyrogram.raw.functions.messages.DeleteHistory>`
            - :obj:`messages.ReadMentions <pyrogram.raw.functions.messages.ReadMentions>`
            - :obj:`messages.UnpinAllMessages <pyrogram.raw.functions.messages.UnpinAllMessages>`
            - :obj:`messages.ReadReactions <pyrogram.raw.functions.messages.ReadReactions>`
            - :obj:`messages.DeleteSavedHistory <pyrogram.raw.functions.messages.DeleteSavedHistory>`
            - :obj:`channels.DeleteParticipantHistory <pyrogram.raw.functions.channels.DeleteParticipantHistory>`
            - :obj:`channels.DeleteTopicHistory <pyrogram.raw.functions.channels.DeleteTopicHistory>`
"""
