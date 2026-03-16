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
    PrivacyKey = Union[raw.types.PrivacyKeyAbout, raw.types.PrivacyKeyAddedByPhone, raw.types.PrivacyKeyBirthday, raw.types.PrivacyKeyChatInvite, raw.types.PrivacyKeyForwards, raw.types.PrivacyKeyNoPaidMessages, raw.types.PrivacyKeyPhoneCall, raw.types.PrivacyKeyPhoneNumber, raw.types.PrivacyKeyPhoneP2P, raw.types.PrivacyKeyProfilePhoto, raw.types.PrivacyKeySavedMusic, raw.types.PrivacyKeyStarGiftsAutoSave, raw.types.PrivacyKeyStatusTimestamp, raw.types.PrivacyKeyVoiceMessages]
else:
    # noinspection PyRedeclaration
    class PrivacyKey(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 14 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PrivacyKeyAbout <pyrogram.raw.types.PrivacyKeyAbout>`
            - :obj:`PrivacyKeyAddedByPhone <pyrogram.raw.types.PrivacyKeyAddedByPhone>`
            - :obj:`PrivacyKeyBirthday <pyrogram.raw.types.PrivacyKeyBirthday>`
            - :obj:`PrivacyKeyChatInvite <pyrogram.raw.types.PrivacyKeyChatInvite>`
            - :obj:`PrivacyKeyForwards <pyrogram.raw.types.PrivacyKeyForwards>`
            - :obj:`PrivacyKeyNoPaidMessages <pyrogram.raw.types.PrivacyKeyNoPaidMessages>`
            - :obj:`PrivacyKeyPhoneCall <pyrogram.raw.types.PrivacyKeyPhoneCall>`
            - :obj:`PrivacyKeyPhoneNumber <pyrogram.raw.types.PrivacyKeyPhoneNumber>`
            - :obj:`PrivacyKeyPhoneP2P <pyrogram.raw.types.PrivacyKeyPhoneP2P>`
            - :obj:`PrivacyKeyProfilePhoto <pyrogram.raw.types.PrivacyKeyProfilePhoto>`
            - :obj:`PrivacyKeySavedMusic <pyrogram.raw.types.PrivacyKeySavedMusic>`
            - :obj:`PrivacyKeyStarGiftsAutoSave <pyrogram.raw.types.PrivacyKeyStarGiftsAutoSave>`
            - :obj:`PrivacyKeyStatusTimestamp <pyrogram.raw.types.PrivacyKeyStatusTimestamp>`
            - :obj:`PrivacyKeyVoiceMessages <pyrogram.raw.types.PrivacyKeyVoiceMessages>`
        """

        QUALNAME = "pyrogram.raw.base.PrivacyKey"
        __union_types__ = Union[raw.types.PrivacyKeyAbout, raw.types.PrivacyKeyAddedByPhone, raw.types.PrivacyKeyBirthday, raw.types.PrivacyKeyChatInvite, raw.types.PrivacyKeyForwards, raw.types.PrivacyKeyNoPaidMessages, raw.types.PrivacyKeyPhoneCall, raw.types.PrivacyKeyPhoneNumber, raw.types.PrivacyKeyPhoneP2P, raw.types.PrivacyKeyProfilePhoto, raw.types.PrivacyKeySavedMusic, raw.types.PrivacyKeyStarGiftsAutoSave, raw.types.PrivacyKeyStatusTimestamp, raw.types.PrivacyKeyVoiceMessages]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.icu/telegram/base/privacy-key")
