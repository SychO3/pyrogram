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
    InputStickerSet = Union[raw.types.InputStickerSetAnimatedEmoji, raw.types.InputStickerSetAnimatedEmojiAnimations, raw.types.InputStickerSetDice, raw.types.InputStickerSetEmojiChannelDefaultStatuses, raw.types.InputStickerSetEmojiDefaultStatuses, raw.types.InputStickerSetEmojiDefaultTopicIcons, raw.types.InputStickerSetEmojiGenericAnimations, raw.types.InputStickerSetEmpty, raw.types.InputStickerSetID, raw.types.InputStickerSetPremiumGifts, raw.types.InputStickerSetShortName, raw.types.InputStickerSetTonGifts]
else:
    # noinspection PyRedeclaration
    class InputStickerSet(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 12 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputStickerSetAnimatedEmoji <pyrogram.raw.types.InputStickerSetAnimatedEmoji>`
            - :obj:`InputStickerSetAnimatedEmojiAnimations <pyrogram.raw.types.InputStickerSetAnimatedEmojiAnimations>`
            - :obj:`InputStickerSetDice <pyrogram.raw.types.InputStickerSetDice>`
            - :obj:`InputStickerSetEmojiChannelDefaultStatuses <pyrogram.raw.types.InputStickerSetEmojiChannelDefaultStatuses>`
            - :obj:`InputStickerSetEmojiDefaultStatuses <pyrogram.raw.types.InputStickerSetEmojiDefaultStatuses>`
            - :obj:`InputStickerSetEmojiDefaultTopicIcons <pyrogram.raw.types.InputStickerSetEmojiDefaultTopicIcons>`
            - :obj:`InputStickerSetEmojiGenericAnimations <pyrogram.raw.types.InputStickerSetEmojiGenericAnimations>`
            - :obj:`InputStickerSetEmpty <pyrogram.raw.types.InputStickerSetEmpty>`
            - :obj:`InputStickerSetID <pyrogram.raw.types.InputStickerSetID>`
            - :obj:`InputStickerSetPremiumGifts <pyrogram.raw.types.InputStickerSetPremiumGifts>`
            - :obj:`InputStickerSetShortName <pyrogram.raw.types.InputStickerSetShortName>`
            - :obj:`InputStickerSetTonGifts <pyrogram.raw.types.InputStickerSetTonGifts>`
        """

        QUALNAME = "pyrogram.raw.base.InputStickerSet"
        __union_types__ = Union[raw.types.InputStickerSetAnimatedEmoji, raw.types.InputStickerSetAnimatedEmojiAnimations, raw.types.InputStickerSetDice, raw.types.InputStickerSetEmojiChannelDefaultStatuses, raw.types.InputStickerSetEmojiDefaultStatuses, raw.types.InputStickerSetEmojiDefaultTopicIcons, raw.types.InputStickerSetEmojiGenericAnimations, raw.types.InputStickerSetEmpty, raw.types.InputStickerSetID, raw.types.InputStickerSetPremiumGifts, raw.types.InputStickerSetShortName, raw.types.InputStickerSetTonGifts]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.live/telegram/base/input-sticker-set")
