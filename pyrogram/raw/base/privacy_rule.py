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

from typing import TYPE_CHECKING, Union

from pyrogram import raw
from pyrogram.raw.core import BaseTypeMeta


if TYPE_CHECKING:
    PrivacyRule = Union[raw.types.PrivacyValueAllowAll, raw.types.PrivacyValueAllowBots, raw.types.PrivacyValueAllowChatParticipants, raw.types.PrivacyValueAllowCloseFriends, raw.types.PrivacyValueAllowContacts, raw.types.PrivacyValueAllowPremium, raw.types.PrivacyValueAllowUsers, raw.types.PrivacyValueDisallowAll, raw.types.PrivacyValueDisallowBots, raw.types.PrivacyValueDisallowChatParticipants, raw.types.PrivacyValueDisallowContacts, raw.types.PrivacyValueDisallowUsers]
else:
    # noinspection PyRedeclaration
    class PrivacyRule(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 12 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PrivacyValueAllowAll <pyrogram.raw.types.PrivacyValueAllowAll>`
            - :obj:`PrivacyValueAllowBots <pyrogram.raw.types.PrivacyValueAllowBots>`
            - :obj:`PrivacyValueAllowChatParticipants <pyrogram.raw.types.PrivacyValueAllowChatParticipants>`
            - :obj:`PrivacyValueAllowCloseFriends <pyrogram.raw.types.PrivacyValueAllowCloseFriends>`
            - :obj:`PrivacyValueAllowContacts <pyrogram.raw.types.PrivacyValueAllowContacts>`
            - :obj:`PrivacyValueAllowPremium <pyrogram.raw.types.PrivacyValueAllowPremium>`
            - :obj:`PrivacyValueAllowUsers <pyrogram.raw.types.PrivacyValueAllowUsers>`
            - :obj:`PrivacyValueDisallowAll <pyrogram.raw.types.PrivacyValueDisallowAll>`
            - :obj:`PrivacyValueDisallowBots <pyrogram.raw.types.PrivacyValueDisallowBots>`
            - :obj:`PrivacyValueDisallowChatParticipants <pyrogram.raw.types.PrivacyValueDisallowChatParticipants>`
            - :obj:`PrivacyValueDisallowContacts <pyrogram.raw.types.PrivacyValueDisallowContacts>`
            - :obj:`PrivacyValueDisallowUsers <pyrogram.raw.types.PrivacyValueDisallowUsers>`
        """

        QUALNAME = "pyrogram.raw.base.PrivacyRule"
        __union_types__ = Union[raw.types.PrivacyValueAllowAll, raw.types.PrivacyValueAllowBots, raw.types.PrivacyValueAllowChatParticipants, raw.types.PrivacyValueAllowCloseFriends, raw.types.PrivacyValueAllowContacts, raw.types.PrivacyValueAllowPremium, raw.types.PrivacyValueAllowUsers, raw.types.PrivacyValueDisallowAll, raw.types.PrivacyValueDisallowBots, raw.types.PrivacyValueDisallowChatParticipants, raw.types.PrivacyValueDisallowContacts, raw.types.PrivacyValueDisallowUsers]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.icu/telegram/base/privacy-rule")
