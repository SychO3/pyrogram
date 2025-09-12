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
ChannelAdminLogEventAction = Union[raw.types.ChannelAdminLogEventActionChangeAbout, raw.types.ChannelAdminLogEventActionChangeAvailableReactions, raw.types.ChannelAdminLogEventActionChangeEmojiStatus, raw.types.ChannelAdminLogEventActionChangeEmojiStickerSet, raw.types.ChannelAdminLogEventActionChangeHistoryTTL, raw.types.ChannelAdminLogEventActionChangeLinkedChat, raw.types.ChannelAdminLogEventActionChangeLocation, raw.types.ChannelAdminLogEventActionChangePeerColor, raw.types.ChannelAdminLogEventActionChangePhoto, raw.types.ChannelAdminLogEventActionChangeProfilePeerColor, raw.types.ChannelAdminLogEventActionChangeStickerSet, raw.types.ChannelAdminLogEventActionChangeTitle, raw.types.ChannelAdminLogEventActionChangeUsername, raw.types.ChannelAdminLogEventActionChangeUsernames, raw.types.ChannelAdminLogEventActionChangeWallpaper, raw.types.ChannelAdminLogEventActionCreateTopic, raw.types.ChannelAdminLogEventActionDefaultBannedRights, raw.types.ChannelAdminLogEventActionDeleteMessage, raw.types.ChannelAdminLogEventActionDeleteTopic, raw.types.ChannelAdminLogEventActionDiscardGroupCall, raw.types.ChannelAdminLogEventActionEditMessage, raw.types.ChannelAdminLogEventActionEditTopic, raw.types.ChannelAdminLogEventActionExportedInviteDelete, raw.types.ChannelAdminLogEventActionExportedInviteEdit, raw.types.ChannelAdminLogEventActionExportedInviteRevoke, raw.types.ChannelAdminLogEventActionParticipantInvite, raw.types.ChannelAdminLogEventActionParticipantJoin, raw.types.ChannelAdminLogEventActionParticipantJoinByInvite, raw.types.ChannelAdminLogEventActionParticipantJoinByRequest, raw.types.ChannelAdminLogEventActionParticipantLeave, raw.types.ChannelAdminLogEventActionParticipantMute, raw.types.ChannelAdminLogEventActionParticipantSubExtend, raw.types.ChannelAdminLogEventActionParticipantToggleAdmin, raw.types.ChannelAdminLogEventActionParticipantToggleBan, raw.types.ChannelAdminLogEventActionParticipantUnmute, raw.types.ChannelAdminLogEventActionParticipantVolume, raw.types.ChannelAdminLogEventActionPinTopic, raw.types.ChannelAdminLogEventActionSendMessage, raw.types.ChannelAdminLogEventActionStartGroupCall, raw.types.ChannelAdminLogEventActionStopPoll, raw.types.ChannelAdminLogEventActionToggleAntiSpam, raw.types.ChannelAdminLogEventActionToggleAutotranslation, raw.types.ChannelAdminLogEventActionToggleForum, raw.types.ChannelAdminLogEventActionToggleGroupCallSetting, raw.types.ChannelAdminLogEventActionToggleInvites, raw.types.ChannelAdminLogEventActionToggleNoForwards, raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden, raw.types.ChannelAdminLogEventActionToggleSignatureProfiles, raw.types.ChannelAdminLogEventActionToggleSignatures, raw.types.ChannelAdminLogEventActionToggleSlowMode, raw.types.ChannelAdminLogEventActionUpdatePinned]
ChannelAdminLogEventAction.__doc__ = """
    This base type has 51 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelAdminLogEventActionChangeAbout <pyrogram.raw.types.ChannelAdminLogEventActionChangeAbout>`
            - :obj:`ChannelAdminLogEventActionChangeAvailableReactions <pyrogram.raw.types.ChannelAdminLogEventActionChangeAvailableReactions>`
            - :obj:`ChannelAdminLogEventActionChangeEmojiStatus <pyrogram.raw.types.ChannelAdminLogEventActionChangeEmojiStatus>`
            - :obj:`ChannelAdminLogEventActionChangeEmojiStickerSet <pyrogram.raw.types.ChannelAdminLogEventActionChangeEmojiStickerSet>`
            - :obj:`ChannelAdminLogEventActionChangeHistoryTTL <pyrogram.raw.types.ChannelAdminLogEventActionChangeHistoryTTL>`
            - :obj:`ChannelAdminLogEventActionChangeLinkedChat <pyrogram.raw.types.ChannelAdminLogEventActionChangeLinkedChat>`
            - :obj:`ChannelAdminLogEventActionChangeLocation <pyrogram.raw.types.ChannelAdminLogEventActionChangeLocation>`
            - :obj:`ChannelAdminLogEventActionChangePeerColor <pyrogram.raw.types.ChannelAdminLogEventActionChangePeerColor>`
            - :obj:`ChannelAdminLogEventActionChangePhoto <pyrogram.raw.types.ChannelAdminLogEventActionChangePhoto>`
            - :obj:`ChannelAdminLogEventActionChangeProfilePeerColor <pyrogram.raw.types.ChannelAdminLogEventActionChangeProfilePeerColor>`
            - :obj:`ChannelAdminLogEventActionChangeStickerSet <pyrogram.raw.types.ChannelAdminLogEventActionChangeStickerSet>`
            - :obj:`ChannelAdminLogEventActionChangeTitle <pyrogram.raw.types.ChannelAdminLogEventActionChangeTitle>`
            - :obj:`ChannelAdminLogEventActionChangeUsername <pyrogram.raw.types.ChannelAdminLogEventActionChangeUsername>`
            - :obj:`ChannelAdminLogEventActionChangeUsernames <pyrogram.raw.types.ChannelAdminLogEventActionChangeUsernames>`
            - :obj:`ChannelAdminLogEventActionChangeWallpaper <pyrogram.raw.types.ChannelAdminLogEventActionChangeWallpaper>`
            - :obj:`ChannelAdminLogEventActionCreateTopic <pyrogram.raw.types.ChannelAdminLogEventActionCreateTopic>`
            - :obj:`ChannelAdminLogEventActionDefaultBannedRights <pyrogram.raw.types.ChannelAdminLogEventActionDefaultBannedRights>`
            - :obj:`ChannelAdminLogEventActionDeleteMessage <pyrogram.raw.types.ChannelAdminLogEventActionDeleteMessage>`
            - :obj:`ChannelAdminLogEventActionDeleteTopic <pyrogram.raw.types.ChannelAdminLogEventActionDeleteTopic>`
            - :obj:`ChannelAdminLogEventActionDiscardGroupCall <pyrogram.raw.types.ChannelAdminLogEventActionDiscardGroupCall>`
            - :obj:`ChannelAdminLogEventActionEditMessage <pyrogram.raw.types.ChannelAdminLogEventActionEditMessage>`
            - :obj:`ChannelAdminLogEventActionEditTopic <pyrogram.raw.types.ChannelAdminLogEventActionEditTopic>`
            - :obj:`ChannelAdminLogEventActionExportedInviteDelete <pyrogram.raw.types.ChannelAdminLogEventActionExportedInviteDelete>`
            - :obj:`ChannelAdminLogEventActionExportedInviteEdit <pyrogram.raw.types.ChannelAdminLogEventActionExportedInviteEdit>`
            - :obj:`ChannelAdminLogEventActionExportedInviteRevoke <pyrogram.raw.types.ChannelAdminLogEventActionExportedInviteRevoke>`
            - :obj:`ChannelAdminLogEventActionParticipantInvite <pyrogram.raw.types.ChannelAdminLogEventActionParticipantInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantJoin <pyrogram.raw.types.ChannelAdminLogEventActionParticipantJoin>`
            - :obj:`ChannelAdminLogEventActionParticipantJoinByInvite <pyrogram.raw.types.ChannelAdminLogEventActionParticipantJoinByInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantJoinByRequest <pyrogram.raw.types.ChannelAdminLogEventActionParticipantJoinByRequest>`
            - :obj:`ChannelAdminLogEventActionParticipantLeave <pyrogram.raw.types.ChannelAdminLogEventActionParticipantLeave>`
            - :obj:`ChannelAdminLogEventActionParticipantMute <pyrogram.raw.types.ChannelAdminLogEventActionParticipantMute>`
            - :obj:`ChannelAdminLogEventActionParticipantSubExtend <pyrogram.raw.types.ChannelAdminLogEventActionParticipantSubExtend>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleAdmin <pyrogram.raw.types.ChannelAdminLogEventActionParticipantToggleAdmin>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleBan <pyrogram.raw.types.ChannelAdminLogEventActionParticipantToggleBan>`
            - :obj:`ChannelAdminLogEventActionParticipantUnmute <pyrogram.raw.types.ChannelAdminLogEventActionParticipantUnmute>`
            - :obj:`ChannelAdminLogEventActionParticipantVolume <pyrogram.raw.types.ChannelAdminLogEventActionParticipantVolume>`
            - :obj:`ChannelAdminLogEventActionPinTopic <pyrogram.raw.types.ChannelAdminLogEventActionPinTopic>`
            - :obj:`ChannelAdminLogEventActionSendMessage <pyrogram.raw.types.ChannelAdminLogEventActionSendMessage>`
            - :obj:`ChannelAdminLogEventActionStartGroupCall <pyrogram.raw.types.ChannelAdminLogEventActionStartGroupCall>`
            - :obj:`ChannelAdminLogEventActionStopPoll <pyrogram.raw.types.ChannelAdminLogEventActionStopPoll>`
            - :obj:`ChannelAdminLogEventActionToggleAntiSpam <pyrogram.raw.types.ChannelAdminLogEventActionToggleAntiSpam>`
            - :obj:`ChannelAdminLogEventActionToggleAutotranslation <pyrogram.raw.types.ChannelAdminLogEventActionToggleAutotranslation>`
            - :obj:`ChannelAdminLogEventActionToggleForum <pyrogram.raw.types.ChannelAdminLogEventActionToggleForum>`
            - :obj:`ChannelAdminLogEventActionToggleGroupCallSetting <pyrogram.raw.types.ChannelAdminLogEventActionToggleGroupCallSetting>`
            - :obj:`ChannelAdminLogEventActionToggleInvites <pyrogram.raw.types.ChannelAdminLogEventActionToggleInvites>`
            - :obj:`ChannelAdminLogEventActionToggleNoForwards <pyrogram.raw.types.ChannelAdminLogEventActionToggleNoForwards>`
            - :obj:`ChannelAdminLogEventActionTogglePreHistoryHidden <pyrogram.raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden>`
            - :obj:`ChannelAdminLogEventActionToggleSignatureProfiles <pyrogram.raw.types.ChannelAdminLogEventActionToggleSignatureProfiles>`
            - :obj:`ChannelAdminLogEventActionToggleSignatures <pyrogram.raw.types.ChannelAdminLogEventActionToggleSignatures>`
            - :obj:`ChannelAdminLogEventActionToggleSlowMode <pyrogram.raw.types.ChannelAdminLogEventActionToggleSlowMode>`
            - :obj:`ChannelAdminLogEventActionUpdatePinned <pyrogram.raw.types.ChannelAdminLogEventActionUpdatePinned>`
"""
