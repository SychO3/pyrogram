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
Chats = Union[raw.types.messages.Chats, raw.types.messages.ChatsSlice]
Chats.__doc__ = """
    This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.Chats <pyrogram.raw.types.messages.Chats>`
            - :obj:`messages.ChatsSlice <pyrogram.raw.types.messages.ChatsSlice>`

    See Also:
        This object can be returned by 8 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChats <pyrogram.raw.functions.messages.GetChats>`
            - :obj:`messages.GetCommonChats <pyrogram.raw.functions.messages.GetCommonChats>`
            - :obj:`channels.GetChannels <pyrogram.raw.functions.channels.GetChannels>`
            - :obj:`channels.GetAdminedPublicChannels <pyrogram.raw.functions.channels.GetAdminedPublicChannels>`
            - :obj:`channels.GetLeftChannels <pyrogram.raw.functions.channels.GetLeftChannels>`
            - :obj:`channels.GetGroupsForDiscussion <pyrogram.raw.functions.channels.GetGroupsForDiscussion>`
            - :obj:`channels.GetChannelRecommendations <pyrogram.raw.functions.channels.GetChannelRecommendations>`
            - :obj:`stories.GetChatsToSend <pyrogram.raw.functions.stories.GetChatsToSend>`
"""
