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
    InputPrivacyKey = Union[raw.types.InputPrivacyKeyAbout, raw.types.InputPrivacyKeyAddedByPhone, raw.types.InputPrivacyKeyBirthday, raw.types.InputPrivacyKeyChatInvite, raw.types.InputPrivacyKeyForwards, raw.types.InputPrivacyKeyNoPaidMessages, raw.types.InputPrivacyKeyPhoneCall, raw.types.InputPrivacyKeyPhoneNumber, raw.types.InputPrivacyKeyPhoneP2P, raw.types.InputPrivacyKeyProfilePhoto, raw.types.InputPrivacyKeySavedMusic, raw.types.InputPrivacyKeyStarGiftsAutoSave, raw.types.InputPrivacyKeyStatusTimestamp, raw.types.InputPrivacyKeyVoiceMessages]
else:
    # noinspection PyRedeclaration
    class InputPrivacyKey(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 14 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPrivacyKeyAbout <pyrogram.raw.types.InputPrivacyKeyAbout>`
            - :obj:`InputPrivacyKeyAddedByPhone <pyrogram.raw.types.InputPrivacyKeyAddedByPhone>`
            - :obj:`InputPrivacyKeyBirthday <pyrogram.raw.types.InputPrivacyKeyBirthday>`
            - :obj:`InputPrivacyKeyChatInvite <pyrogram.raw.types.InputPrivacyKeyChatInvite>`
            - :obj:`InputPrivacyKeyForwards <pyrogram.raw.types.InputPrivacyKeyForwards>`
            - :obj:`InputPrivacyKeyNoPaidMessages <pyrogram.raw.types.InputPrivacyKeyNoPaidMessages>`
            - :obj:`InputPrivacyKeyPhoneCall <pyrogram.raw.types.InputPrivacyKeyPhoneCall>`
            - :obj:`InputPrivacyKeyPhoneNumber <pyrogram.raw.types.InputPrivacyKeyPhoneNumber>`
            - :obj:`InputPrivacyKeyPhoneP2P <pyrogram.raw.types.InputPrivacyKeyPhoneP2P>`
            - :obj:`InputPrivacyKeyProfilePhoto <pyrogram.raw.types.InputPrivacyKeyProfilePhoto>`
            - :obj:`InputPrivacyKeySavedMusic <pyrogram.raw.types.InputPrivacyKeySavedMusic>`
            - :obj:`InputPrivacyKeyStarGiftsAutoSave <pyrogram.raw.types.InputPrivacyKeyStarGiftsAutoSave>`
            - :obj:`InputPrivacyKeyStatusTimestamp <pyrogram.raw.types.InputPrivacyKeyStatusTimestamp>`
            - :obj:`InputPrivacyKeyVoiceMessages <pyrogram.raw.types.InputPrivacyKeyVoiceMessages>`
        """

        QUALNAME = "pyrogram.raw.base.InputPrivacyKey"
        __union_types__ = Union[raw.types.InputPrivacyKeyAbout, raw.types.InputPrivacyKeyAddedByPhone, raw.types.InputPrivacyKeyBirthday, raw.types.InputPrivacyKeyChatInvite, raw.types.InputPrivacyKeyForwards, raw.types.InputPrivacyKeyNoPaidMessages, raw.types.InputPrivacyKeyPhoneCall, raw.types.InputPrivacyKeyPhoneNumber, raw.types.InputPrivacyKeyPhoneP2P, raw.types.InputPrivacyKeyProfilePhoto, raw.types.InputPrivacyKeySavedMusic, raw.types.InputPrivacyKeyStarGiftsAutoSave, raw.types.InputPrivacyKeyStatusTimestamp, raw.types.InputPrivacyKeyVoiceMessages]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.icu/telegram/base/input-privacy-key")
