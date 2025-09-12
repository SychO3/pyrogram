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
InputPrivacyRule = Union[raw.types.InputPrivacyValueAllowAll, raw.types.InputPrivacyValueAllowBots, raw.types.InputPrivacyValueAllowChatParticipants, raw.types.InputPrivacyValueAllowCloseFriends, raw.types.InputPrivacyValueAllowContacts, raw.types.InputPrivacyValueAllowPremium, raw.types.InputPrivacyValueAllowUsers, raw.types.InputPrivacyValueDisallowAll, raw.types.InputPrivacyValueDisallowBots, raw.types.InputPrivacyValueDisallowChatParticipants, raw.types.InputPrivacyValueDisallowContacts, raw.types.InputPrivacyValueDisallowUsers]
InputPrivacyRule.__doc__ = """
    This base type has 12 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPrivacyValueAllowAll <pyrogram.raw.types.InputPrivacyValueAllowAll>`
            - :obj:`InputPrivacyValueAllowBots <pyrogram.raw.types.InputPrivacyValueAllowBots>`
            - :obj:`InputPrivacyValueAllowChatParticipants <pyrogram.raw.types.InputPrivacyValueAllowChatParticipants>`
            - :obj:`InputPrivacyValueAllowCloseFriends <pyrogram.raw.types.InputPrivacyValueAllowCloseFriends>`
            - :obj:`InputPrivacyValueAllowContacts <pyrogram.raw.types.InputPrivacyValueAllowContacts>`
            - :obj:`InputPrivacyValueAllowPremium <pyrogram.raw.types.InputPrivacyValueAllowPremium>`
            - :obj:`InputPrivacyValueAllowUsers <pyrogram.raw.types.InputPrivacyValueAllowUsers>`
            - :obj:`InputPrivacyValueDisallowAll <pyrogram.raw.types.InputPrivacyValueDisallowAll>`
            - :obj:`InputPrivacyValueDisallowBots <pyrogram.raw.types.InputPrivacyValueDisallowBots>`
            - :obj:`InputPrivacyValueDisallowChatParticipants <pyrogram.raw.types.InputPrivacyValueDisallowChatParticipants>`
            - :obj:`InputPrivacyValueDisallowContacts <pyrogram.raw.types.InputPrivacyValueDisallowContacts>`
            - :obj:`InputPrivacyValueDisallowUsers <pyrogram.raw.types.InputPrivacyValueDisallowUsers>`
"""
