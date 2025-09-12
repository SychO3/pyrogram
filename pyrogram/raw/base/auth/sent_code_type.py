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
SentCodeType = Union[raw.types.auth.SentCodeTypeApp, raw.types.auth.SentCodeTypeCall, raw.types.auth.SentCodeTypeEmailCode, raw.types.auth.SentCodeTypeFirebaseSms, raw.types.auth.SentCodeTypeFlashCall, raw.types.auth.SentCodeTypeFragmentSms, raw.types.auth.SentCodeTypeMissedCall, raw.types.auth.SentCodeTypeSetUpEmailRequired, raw.types.auth.SentCodeTypeSms, raw.types.auth.SentCodeTypeSmsPhrase, raw.types.auth.SentCodeTypeSmsWord]
SentCodeType.__doc__ = """
    This base type has 11 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.SentCodeTypeApp <pyrogram.raw.types.auth.SentCodeTypeApp>`
            - :obj:`auth.SentCodeTypeCall <pyrogram.raw.types.auth.SentCodeTypeCall>`
            - :obj:`auth.SentCodeTypeEmailCode <pyrogram.raw.types.auth.SentCodeTypeEmailCode>`
            - :obj:`auth.SentCodeTypeFirebaseSms <pyrogram.raw.types.auth.SentCodeTypeFirebaseSms>`
            - :obj:`auth.SentCodeTypeFlashCall <pyrogram.raw.types.auth.SentCodeTypeFlashCall>`
            - :obj:`auth.SentCodeTypeFragmentSms <pyrogram.raw.types.auth.SentCodeTypeFragmentSms>`
            - :obj:`auth.SentCodeTypeMissedCall <pyrogram.raw.types.auth.SentCodeTypeMissedCall>`
            - :obj:`auth.SentCodeTypeSetUpEmailRequired <pyrogram.raw.types.auth.SentCodeTypeSetUpEmailRequired>`
            - :obj:`auth.SentCodeTypeSms <pyrogram.raw.types.auth.SentCodeTypeSms>`
            - :obj:`auth.SentCodeTypeSmsPhrase <pyrogram.raw.types.auth.SentCodeTypeSmsPhrase>`
            - :obj:`auth.SentCodeTypeSmsWord <pyrogram.raw.types.auth.SentCodeTypeSmsWord>`
"""
