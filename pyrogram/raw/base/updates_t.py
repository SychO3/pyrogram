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
    Updates = Union[raw.types.UpdateShort, raw.types.UpdateShortChatMessage, raw.types.UpdateShortMessage, raw.types.UpdateShortSentMessage, raw.types.Updates, raw.types.UpdatesCombined, raw.types.UpdatesTooLong]
else:
    # noinspection PyRedeclaration
    class Updates(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateShort <pyrogram.raw.types.UpdateShort>`
            - :obj:`UpdateShortChatMessage <pyrogram.raw.types.UpdateShortChatMessage>`
            - :obj:`UpdateShortMessage <pyrogram.raw.types.UpdateShortMessage>`
            - :obj:`UpdateShortSentMessage <pyrogram.raw.types.UpdateShortSentMessage>`
            - :obj:`Updates <pyrogram.raw.types.Updates>`
            - :obj:`UpdatesCombined <pyrogram.raw.types.UpdatesCombined>`
            - :obj:`UpdatesTooLong <pyrogram.raw.types.UpdatesTooLong>`

    See Also:
        This object can be returned by 124 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifyExceptions <pyrogram.raw.functions.account.GetNotifyExceptions>`
            - :obj:`account.UpdateConnectedBot <pyrogram.raw.functions.account.UpdateConnectedBot>`
            - :obj:`account.GetBotBusinessConnection <pyrogram.raw.functions.account.GetBotBusinessConnection>`
            - :obj:`users.SuggestBirthday <pyrogram.raw.functions.users.SuggestBirthday>`
            - :obj:`contacts.DeleteContacts <pyrogram.raw.functions.contacts.DeleteContacts>`
            - :obj:`contacts.AddContact <pyrogram.raw.functions.contacts.AddContact>`
            - :obj:`contacts.AcceptContact <pyrogram.raw.functions.contacts.AcceptContact>`
            - :obj:`contacts.GetLocated <pyrogram.raw.functions.contacts.GetLocated>`
            - :obj:`contacts.BlockFromReplies <pyrogram.raw.functions.contacts.BlockFromReplies>`
            - :obj:`messages.SendMessage <pyrogram.raw.functions.messages.SendMessage>`
            - :obj:`messages.SendMedia <pyrogram.raw.functions.messages.SendMedia>`
            - :obj:`messages.ForwardMessages <pyrogram.raw.functions.messages.ForwardMessages>`
            - :obj:`messages.EditChatTitle <pyrogram.raw.functions.messages.EditChatTitle>`
            - :obj:`messages.EditChatPhoto <pyrogram.raw.functions.messages.EditChatPhoto>`
            - :obj:`messages.DeleteChatUser <pyrogram.raw.functions.messages.DeleteChatUser>`
            - :obj:`messages.ImportChatInvite <pyrogram.raw.functions.messages.ImportChatInvite>`
            - :obj:`messages.StartBot <pyrogram.raw.functions.messages.StartBot>`
            - :obj:`messages.MigrateChat <pyrogram.raw.functions.messages.MigrateChat>`
            - :obj:`messages.SendInlineBotResult <pyrogram.raw.functions.messages.SendInlineBotResult>`
            - :obj:`messages.EditMessage <pyrogram.raw.functions.messages.EditMessage>`
            - :obj:`messages.GetAllDrafts <pyrogram.raw.functions.messages.GetAllDrafts>`
            - :obj:`messages.SetGameScore <pyrogram.raw.functions.messages.SetGameScore>`
            - :obj:`messages.SendScreenshotNotification <pyrogram.raw.functions.messages.SendScreenshotNotification>`
            - :obj:`messages.SendMultiMedia <pyrogram.raw.functions.messages.SendMultiMedia>`
            - :obj:`messages.UpdatePinnedMessage <pyrogram.raw.functions.messages.UpdatePinnedMessage>`
            - :obj:`messages.SendVote <pyrogram.raw.functions.messages.SendVote>`
            - :obj:`messages.GetPollResults <pyrogram.raw.functions.messages.GetPollResults>`
            - :obj:`messages.EditChatDefaultBannedRights <pyrogram.raw.functions.messages.EditChatDefaultBannedRights>`
            - :obj:`messages.SendScheduledMessages <pyrogram.raw.functions.messages.SendScheduledMessages>`
            - :obj:`messages.DeleteScheduledMessages <pyrogram.raw.functions.messages.DeleteScheduledMessages>`
            - :obj:`messages.SetHistoryTTL <pyrogram.raw.functions.messages.SetHistoryTTL>`
            - :obj:`messages.SetChatTheme <pyrogram.raw.functions.messages.SetChatTheme>`
            - :obj:`messages.HideChatJoinRequest <pyrogram.raw.functions.messages.HideChatJoinRequest>`
            - :obj:`messages.HideAllChatJoinRequests <pyrogram.raw.functions.messages.HideAllChatJoinRequests>`
            - :obj:`messages.ToggleNoForwards <pyrogram.raw.functions.messages.ToggleNoForwards>`
            - :obj:`messages.SendReaction <pyrogram.raw.functions.messages.SendReaction>`
            - :obj:`messages.GetMessagesReactions <pyrogram.raw.functions.messages.GetMessagesReactions>`
            - :obj:`messages.SetChatAvailableReactions <pyrogram.raw.functions.messages.SetChatAvailableReactions>`
            - :obj:`messages.SendWebViewData <pyrogram.raw.functions.messages.SendWebViewData>`
            - :obj:`messages.GetExtendedMedia <pyrogram.raw.functions.messages.GetExtendedMedia>`
            - :obj:`messages.SendBotRequestedPeer <pyrogram.raw.functions.messages.SendBotRequestedPeer>`
            - :obj:`messages.SetChatWallPaper <pyrogram.raw.functions.messages.SetChatWallPaper>`
            - :obj:`messages.SendQuickReplyMessages <pyrogram.raw.functions.messages.SendQuickReplyMessages>`
            - :obj:`messages.DeleteQuickReplyMessages <pyrogram.raw.functions.messages.DeleteQuickReplyMessages>`
            - :obj:`messages.EditFactCheck <pyrogram.raw.functions.messages.EditFactCheck>`
            - :obj:`messages.DeleteFactCheck <pyrogram.raw.functions.messages.DeleteFactCheck>`
            - :obj:`messages.SendPaidReaction <pyrogram.raw.functions.messages.SendPaidReaction>`
            - :obj:`messages.GetPaidReactionPrivacy <pyrogram.raw.functions.messages.GetPaidReactionPrivacy>`
            - :obj:`messages.ToggleTodoCompleted <pyrogram.raw.functions.messages.ToggleTodoCompleted>`
            - :obj:`messages.AppendTodoList <pyrogram.raw.functions.messages.AppendTodoList>`
            - :obj:`messages.ToggleSuggestedPostApproval <pyrogram.raw.functions.messages.ToggleSuggestedPostApproval>`
            - :obj:`messages.EditForumTopic <pyrogram.raw.functions.messages.EditForumTopic>`
            - :obj:`messages.UpdatePinnedForumTopic <pyrogram.raw.functions.messages.UpdatePinnedForumTopic>`
            - :obj:`messages.ReorderPinnedForumTopics <pyrogram.raw.functions.messages.ReorderPinnedForumTopics>`
            - :obj:`messages.CreateForumTopic <pyrogram.raw.functions.messages.CreateForumTopic>`
            - :obj:`channels.CreateChannel <pyrogram.raw.functions.channels.CreateChannel>`
            - :obj:`channels.EditAdmin <pyrogram.raw.functions.channels.EditAdmin>`
            - :obj:`channels.EditTitle <pyrogram.raw.functions.channels.EditTitle>`
            - :obj:`channels.EditPhoto <pyrogram.raw.functions.channels.EditPhoto>`
            - :obj:`channels.JoinChannel <pyrogram.raw.functions.channels.JoinChannel>`
            - :obj:`channels.LeaveChannel <pyrogram.raw.functions.channels.LeaveChannel>`
            - :obj:`channels.DeleteChannel <pyrogram.raw.functions.channels.DeleteChannel>`
            - :obj:`channels.ToggleSignatures <pyrogram.raw.functions.channels.ToggleSignatures>`
            - :obj:`channels.EditBanned <pyrogram.raw.functions.channels.EditBanned>`
            - :obj:`channels.DeleteHistory <pyrogram.raw.functions.channels.DeleteHistory>`
            - :obj:`channels.TogglePreHistoryHidden <pyrogram.raw.functions.channels.TogglePreHistoryHidden>`
            - :obj:`channels.EditCreator <pyrogram.raw.functions.channels.EditCreator>`
            - :obj:`channels.ToggleSlowMode <pyrogram.raw.functions.channels.ToggleSlowMode>`
            - :obj:`channels.ConvertToGigagroup <pyrogram.raw.functions.channels.ConvertToGigagroup>`
            - :obj:`channels.ToggleJoinToSend <pyrogram.raw.functions.channels.ToggleJoinToSend>`
            - :obj:`channels.ToggleJoinRequest <pyrogram.raw.functions.channels.ToggleJoinRequest>`
            - :obj:`channels.ToggleForum <pyrogram.raw.functions.channels.ToggleForum>`
            - :obj:`channels.ToggleAntiSpam <pyrogram.raw.functions.channels.ToggleAntiSpam>`
            - :obj:`channels.ToggleParticipantsHidden <pyrogram.raw.functions.channels.ToggleParticipantsHidden>`
            - :obj:`channels.UpdateColor <pyrogram.raw.functions.channels.UpdateColor>`
            - :obj:`channels.ToggleViewForumAsMessages <pyrogram.raw.functions.channels.ToggleViewForumAsMessages>`
            - :obj:`channels.UpdateEmojiStatus <pyrogram.raw.functions.channels.UpdateEmojiStatus>`
            - :obj:`channels.SetBoostsToUnblockRestrictions <pyrogram.raw.functions.channels.SetBoostsToUnblockRestrictions>`
            - :obj:`channels.RestrictSponsoredMessages <pyrogram.raw.functions.channels.RestrictSponsoredMessages>`
            - :obj:`channels.UpdatePaidMessagesPrice <pyrogram.raw.functions.channels.UpdatePaidMessagesPrice>`
            - :obj:`channels.ToggleAutotranslation <pyrogram.raw.functions.channels.ToggleAutotranslation>`
            - :obj:`bots.AllowSendMessage <pyrogram.raw.functions.bots.AllowSendMessage>`
            - :obj:`payments.AssignAppStoreTransaction <pyrogram.raw.functions.payments.AssignAppStoreTransaction>`
            - :obj:`payments.AssignPlayMarketTransaction <pyrogram.raw.functions.payments.AssignPlayMarketTransaction>`
            - :obj:`payments.ApplyGiftCode <pyrogram.raw.functions.payments.ApplyGiftCode>`
            - :obj:`payments.LaunchPrepaidGiveaway <pyrogram.raw.functions.payments.LaunchPrepaidGiveaway>`
            - :obj:`payments.RefundStarsCharge <pyrogram.raw.functions.payments.RefundStarsCharge>`
            - :obj:`payments.UpgradeStarGift <pyrogram.raw.functions.payments.UpgradeStarGift>`
            - :obj:`payments.TransferStarGift <pyrogram.raw.functions.payments.TransferStarGift>`
            - :obj:`payments.UpdateStarGiftPrice <pyrogram.raw.functions.payments.UpdateStarGiftPrice>`
            - :obj:`phone.DiscardCall <pyrogram.raw.functions.phone.DiscardCall>`
            - :obj:`phone.SetCallRating <pyrogram.raw.functions.phone.SetCallRating>`
            - :obj:`phone.CreateGroupCall <pyrogram.raw.functions.phone.CreateGroupCall>`
            - :obj:`phone.JoinGroupCall <pyrogram.raw.functions.phone.JoinGroupCall>`
            - :obj:`phone.LeaveGroupCall <pyrogram.raw.functions.phone.LeaveGroupCall>`
            - :obj:`phone.InviteToGroupCall <pyrogram.raw.functions.phone.InviteToGroupCall>`
            - :obj:`phone.DiscardGroupCall <pyrogram.raw.functions.phone.DiscardGroupCall>`
            - :obj:`phone.ToggleGroupCallSettings <pyrogram.raw.functions.phone.ToggleGroupCallSettings>`
            - :obj:`phone.ToggleGroupCallRecord <pyrogram.raw.functions.phone.ToggleGroupCallRecord>`
            - :obj:`phone.EditGroupCallParticipant <pyrogram.raw.functions.phone.EditGroupCallParticipant>`
            - :obj:`phone.EditGroupCallTitle <pyrogram.raw.functions.phone.EditGroupCallTitle>`
            - :obj:`phone.ToggleGroupCallStartSubscription <pyrogram.raw.functions.phone.ToggleGroupCallStartSubscription>`
            - :obj:`phone.StartScheduledGroupCall <pyrogram.raw.functions.phone.StartScheduledGroupCall>`
            - :obj:`phone.JoinGroupCallPresentation <pyrogram.raw.functions.phone.JoinGroupCallPresentation>`
            - :obj:`phone.LeaveGroupCallPresentation <pyrogram.raw.functions.phone.LeaveGroupCallPresentation>`
            - :obj:`phone.CreateConferenceCall <pyrogram.raw.functions.phone.CreateConferenceCall>`
            - :obj:`phone.DeleteConferenceCallParticipants <pyrogram.raw.functions.phone.DeleteConferenceCallParticipants>`
            - :obj:`phone.SendConferenceCallBroadcast <pyrogram.raw.functions.phone.SendConferenceCallBroadcast>`
            - :obj:`phone.InviteConferenceCallParticipant <pyrogram.raw.functions.phone.InviteConferenceCallParticipant>`
            - :obj:`phone.DeclineConferenceCallInvite <pyrogram.raw.functions.phone.DeclineConferenceCallInvite>`
            - :obj:`phone.GetGroupCallChainBlocks <pyrogram.raw.functions.phone.GetGroupCallChainBlocks>`
            - :obj:`phone.SendGroupCallMessage <pyrogram.raw.functions.phone.SendGroupCallMessage>`
            - :obj:`phone.DeleteGroupCallMessages <pyrogram.raw.functions.phone.DeleteGroupCallMessages>`
            - :obj:`phone.DeleteGroupCallParticipantMessages <pyrogram.raw.functions.phone.DeleteGroupCallParticipantMessages>`
            - :obj:`folders.EditPeerFolders <pyrogram.raw.functions.folders.EditPeerFolders>`
            - :obj:`chatlists.JoinChatlistInvite <pyrogram.raw.functions.chatlists.JoinChatlistInvite>`
            - :obj:`chatlists.JoinChatlistUpdates <pyrogram.raw.functions.chatlists.JoinChatlistUpdates>`
            - :obj:`chatlists.LeaveChatlist <pyrogram.raw.functions.chatlists.LeaveChatlist>`
            - :obj:`stories.SendStory <pyrogram.raw.functions.stories.SendStory>`
            - :obj:`stories.EditStory <pyrogram.raw.functions.stories.EditStory>`
            - :obj:`stories.ActivateStealthMode <pyrogram.raw.functions.stories.ActivateStealthMode>`
            - :obj:`stories.SendReaction <pyrogram.raw.functions.stories.SendReaction>`
            - :obj:`stories.GetAllReadPeerStories <pyrogram.raw.functions.stories.GetAllReadPeerStories>`
            - :obj:`stories.StartLive <pyrogram.raw.functions.stories.StartLive>`
        """

        QUALNAME = "pyrogram.raw.base.Updates"
        __union_types__ = Union[raw.types.UpdateShort, raw.types.UpdateShortChatMessage, raw.types.UpdateShortMessage, raw.types.UpdateShortSentMessage, raw.types.Updates, raw.types.UpdatesCombined, raw.types.UpdatesTooLong]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.live/telegram/base/updates")
