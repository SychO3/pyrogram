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
    Update = Union[raw.types.UpdateAttachMenuBots, raw.types.UpdateAutoSaveSettings, raw.types.UpdateBotBusinessConnect, raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotChatBoost, raw.types.UpdateBotChatInviteRequester, raw.types.UpdateBotCommands, raw.types.UpdateBotDeleteBusinessMessage, raw.types.UpdateBotEditBusinessMessage, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend, raw.types.UpdateBotMenuButton, raw.types.UpdateBotMessageReaction, raw.types.UpdateBotMessageReactions, raw.types.UpdateBotNewBusinessMessage, raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotPurchasedPaidMedia, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotStopped, raw.types.UpdateBotWebhookJSON, raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateBusinessBotCallbackQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages, raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant, raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping, raw.types.UpdateChannelViewForumAsMessages, raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights, raw.types.UpdateChatParticipant, raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete, raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig, raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages, raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteQuickReply, raw.types.UpdateDeleteQuickReplyMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter, raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned, raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage, raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead, raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers, raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallChainBlocks, raw.types.UpdateGroupCallConnection, raw.types.UpdateGroupCallEncryptedMessage, raw.types.UpdateGroupCallMessage, raw.types.UpdateGroupCallParticipants, raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong, raw.types.UpdateLoginToken, raw.types.UpdateMessageExtendedMedia, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll, raw.types.UpdateMessagePollVote, raw.types.UpdateMessageReactions, raw.types.UpdateMonoForumNoPaidException, raw.types.UpdateMoveStickerSetToTop, raw.types.UpdateNewAuthorization, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage, raw.types.UpdateNewMessage, raw.types.UpdateNewQuickReply, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet, raw.types.UpdateNewStoryReaction, raw.types.UpdateNotifySettings, raw.types.UpdatePaidReactionPrivacy, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerHistoryTTL, raw.types.UpdatePeerLocated, raw.types.UpdatePeerSettings, raw.types.UpdatePeerWallpaper, raw.types.UpdatePendingJoinRequests, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData, raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedForumTopic, raw.types.UpdatePinnedForumTopics, raw.types.UpdatePinnedMessages, raw.types.UpdatePinnedSavedDialogs, raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateQuickReplies, raw.types.UpdateQuickReplyMessage, raw.types.UpdateReadChannelDiscussionInbox, raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox, raw.types.UpdateReadFeaturedEmojiStickers, raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox, raw.types.UpdateReadMessagesContents, raw.types.UpdateReadMonoForumInbox, raw.types.UpdateReadMonoForumOutbox, raw.types.UpdateReadStories, raw.types.UpdateRecentEmojiStatuses, raw.types.UpdateRecentReactions, raw.types.UpdateRecentStickers, raw.types.UpdateSavedDialogPinned, raw.types.UpdateSavedGifs, raw.types.UpdateSavedReactionTags, raw.types.UpdateSavedRingtones, raw.types.UpdateSentPhoneCode, raw.types.UpdateSentStoryReaction, raw.types.UpdateServiceNotification, raw.types.UpdateSmsJob, raw.types.UpdateStarsBalance, raw.types.UpdateStarsRevenueStatus, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder, raw.types.UpdateStoriesStealthMode, raw.types.UpdateStory, raw.types.UpdateStoryID, raw.types.UpdateTheme, raw.types.UpdateTranscribedAudio, raw.types.UpdateUser, raw.types.UpdateUserEmojiStatus, raw.types.UpdateUserName, raw.types.UpdateUserPhone, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping, raw.types.UpdateWebPage, raw.types.UpdateWebViewResultSent]
else:
    # noinspection PyRedeclaration
    class Update(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 147 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateAttachMenuBots <pyrogram.raw.types.UpdateAttachMenuBots>`
            - :obj:`UpdateAutoSaveSettings <pyrogram.raw.types.UpdateAutoSaveSettings>`
            - :obj:`UpdateBotBusinessConnect <pyrogram.raw.types.UpdateBotBusinessConnect>`
            - :obj:`UpdateBotCallbackQuery <pyrogram.raw.types.UpdateBotCallbackQuery>`
            - :obj:`UpdateBotChatBoost <pyrogram.raw.types.UpdateBotChatBoost>`
            - :obj:`UpdateBotChatInviteRequester <pyrogram.raw.types.UpdateBotChatInviteRequester>`
            - :obj:`UpdateBotCommands <pyrogram.raw.types.UpdateBotCommands>`
            - :obj:`UpdateBotDeleteBusinessMessage <pyrogram.raw.types.UpdateBotDeleteBusinessMessage>`
            - :obj:`UpdateBotEditBusinessMessage <pyrogram.raw.types.UpdateBotEditBusinessMessage>`
            - :obj:`UpdateBotInlineQuery <pyrogram.raw.types.UpdateBotInlineQuery>`
            - :obj:`UpdateBotInlineSend <pyrogram.raw.types.UpdateBotInlineSend>`
            - :obj:`UpdateBotMenuButton <pyrogram.raw.types.UpdateBotMenuButton>`
            - :obj:`UpdateBotMessageReaction <pyrogram.raw.types.UpdateBotMessageReaction>`
            - :obj:`UpdateBotMessageReactions <pyrogram.raw.types.UpdateBotMessageReactions>`
            - :obj:`UpdateBotNewBusinessMessage <pyrogram.raw.types.UpdateBotNewBusinessMessage>`
            - :obj:`UpdateBotPrecheckoutQuery <pyrogram.raw.types.UpdateBotPrecheckoutQuery>`
            - :obj:`UpdateBotPurchasedPaidMedia <pyrogram.raw.types.UpdateBotPurchasedPaidMedia>`
            - :obj:`UpdateBotShippingQuery <pyrogram.raw.types.UpdateBotShippingQuery>`
            - :obj:`UpdateBotStopped <pyrogram.raw.types.UpdateBotStopped>`
            - :obj:`UpdateBotWebhookJSON <pyrogram.raw.types.UpdateBotWebhookJSON>`
            - :obj:`UpdateBotWebhookJSONQuery <pyrogram.raw.types.UpdateBotWebhookJSONQuery>`
            - :obj:`UpdateBusinessBotCallbackQuery <pyrogram.raw.types.UpdateBusinessBotCallbackQuery>`
            - :obj:`UpdateChannel <pyrogram.raw.types.UpdateChannel>`
            - :obj:`UpdateChannelAvailableMessages <pyrogram.raw.types.UpdateChannelAvailableMessages>`
            - :obj:`UpdateChannelMessageForwards <pyrogram.raw.types.UpdateChannelMessageForwards>`
            - :obj:`UpdateChannelMessageViews <pyrogram.raw.types.UpdateChannelMessageViews>`
            - :obj:`UpdateChannelParticipant <pyrogram.raw.types.UpdateChannelParticipant>`
            - :obj:`UpdateChannelReadMessagesContents <pyrogram.raw.types.UpdateChannelReadMessagesContents>`
            - :obj:`UpdateChannelTooLong <pyrogram.raw.types.UpdateChannelTooLong>`
            - :obj:`UpdateChannelUserTyping <pyrogram.raw.types.UpdateChannelUserTyping>`
            - :obj:`UpdateChannelViewForumAsMessages <pyrogram.raw.types.UpdateChannelViewForumAsMessages>`
            - :obj:`UpdateChannelWebPage <pyrogram.raw.types.UpdateChannelWebPage>`
            - :obj:`UpdateChat <pyrogram.raw.types.UpdateChat>`
            - :obj:`UpdateChatDefaultBannedRights <pyrogram.raw.types.UpdateChatDefaultBannedRights>`
            - :obj:`UpdateChatParticipant <pyrogram.raw.types.UpdateChatParticipant>`
            - :obj:`UpdateChatParticipantAdd <pyrogram.raw.types.UpdateChatParticipantAdd>`
            - :obj:`UpdateChatParticipantAdmin <pyrogram.raw.types.UpdateChatParticipantAdmin>`
            - :obj:`UpdateChatParticipantDelete <pyrogram.raw.types.UpdateChatParticipantDelete>`
            - :obj:`UpdateChatParticipants <pyrogram.raw.types.UpdateChatParticipants>`
            - :obj:`UpdateChatUserTyping <pyrogram.raw.types.UpdateChatUserTyping>`
            - :obj:`UpdateConfig <pyrogram.raw.types.UpdateConfig>`
            - :obj:`UpdateContactsReset <pyrogram.raw.types.UpdateContactsReset>`
            - :obj:`UpdateDcOptions <pyrogram.raw.types.UpdateDcOptions>`
            - :obj:`UpdateDeleteChannelMessages <pyrogram.raw.types.UpdateDeleteChannelMessages>`
            - :obj:`UpdateDeleteMessages <pyrogram.raw.types.UpdateDeleteMessages>`
            - :obj:`UpdateDeleteQuickReply <pyrogram.raw.types.UpdateDeleteQuickReply>`
            - :obj:`UpdateDeleteQuickReplyMessages <pyrogram.raw.types.UpdateDeleteQuickReplyMessages>`
            - :obj:`UpdateDeleteScheduledMessages <pyrogram.raw.types.UpdateDeleteScheduledMessages>`
            - :obj:`UpdateDialogFilter <pyrogram.raw.types.UpdateDialogFilter>`
            - :obj:`UpdateDialogFilterOrder <pyrogram.raw.types.UpdateDialogFilterOrder>`
            - :obj:`UpdateDialogFilters <pyrogram.raw.types.UpdateDialogFilters>`
            - :obj:`UpdateDialogPinned <pyrogram.raw.types.UpdateDialogPinned>`
            - :obj:`UpdateDialogUnreadMark <pyrogram.raw.types.UpdateDialogUnreadMark>`
            - :obj:`UpdateDraftMessage <pyrogram.raw.types.UpdateDraftMessage>`
            - :obj:`UpdateEditChannelMessage <pyrogram.raw.types.UpdateEditChannelMessage>`
            - :obj:`UpdateEditMessage <pyrogram.raw.types.UpdateEditMessage>`
            - :obj:`UpdateEncryptedChatTyping <pyrogram.raw.types.UpdateEncryptedChatTyping>`
            - :obj:`UpdateEncryptedMessagesRead <pyrogram.raw.types.UpdateEncryptedMessagesRead>`
            - :obj:`UpdateEncryption <pyrogram.raw.types.UpdateEncryption>`
            - :obj:`UpdateFavedStickers <pyrogram.raw.types.UpdateFavedStickers>`
            - :obj:`UpdateFolderPeers <pyrogram.raw.types.UpdateFolderPeers>`
            - :obj:`UpdateGeoLiveViewed <pyrogram.raw.types.UpdateGeoLiveViewed>`
            - :obj:`UpdateGroupCall <pyrogram.raw.types.UpdateGroupCall>`
            - :obj:`UpdateGroupCallChainBlocks <pyrogram.raw.types.UpdateGroupCallChainBlocks>`
            - :obj:`UpdateGroupCallConnection <pyrogram.raw.types.UpdateGroupCallConnection>`
            - :obj:`UpdateGroupCallEncryptedMessage <pyrogram.raw.types.UpdateGroupCallEncryptedMessage>`
            - :obj:`UpdateGroupCallMessage <pyrogram.raw.types.UpdateGroupCallMessage>`
            - :obj:`UpdateGroupCallParticipants <pyrogram.raw.types.UpdateGroupCallParticipants>`
            - :obj:`UpdateInlineBotCallbackQuery <pyrogram.raw.types.UpdateInlineBotCallbackQuery>`
            - :obj:`UpdateLangPack <pyrogram.raw.types.UpdateLangPack>`
            - :obj:`UpdateLangPackTooLong <pyrogram.raw.types.UpdateLangPackTooLong>`
            - :obj:`UpdateLoginToken <pyrogram.raw.types.UpdateLoginToken>`
            - :obj:`UpdateMessageExtendedMedia <pyrogram.raw.types.UpdateMessageExtendedMedia>`
            - :obj:`UpdateMessageID <pyrogram.raw.types.UpdateMessageID>`
            - :obj:`UpdateMessagePoll <pyrogram.raw.types.UpdateMessagePoll>`
            - :obj:`UpdateMessagePollVote <pyrogram.raw.types.UpdateMessagePollVote>`
            - :obj:`UpdateMessageReactions <pyrogram.raw.types.UpdateMessageReactions>`
            - :obj:`UpdateMonoForumNoPaidException <pyrogram.raw.types.UpdateMonoForumNoPaidException>`
            - :obj:`UpdateMoveStickerSetToTop <pyrogram.raw.types.UpdateMoveStickerSetToTop>`
            - :obj:`UpdateNewAuthorization <pyrogram.raw.types.UpdateNewAuthorization>`
            - :obj:`UpdateNewChannelMessage <pyrogram.raw.types.UpdateNewChannelMessage>`
            - :obj:`UpdateNewEncryptedMessage <pyrogram.raw.types.UpdateNewEncryptedMessage>`
            - :obj:`UpdateNewMessage <pyrogram.raw.types.UpdateNewMessage>`
            - :obj:`UpdateNewQuickReply <pyrogram.raw.types.UpdateNewQuickReply>`
            - :obj:`UpdateNewScheduledMessage <pyrogram.raw.types.UpdateNewScheduledMessage>`
            - :obj:`UpdateNewStickerSet <pyrogram.raw.types.UpdateNewStickerSet>`
            - :obj:`UpdateNewStoryReaction <pyrogram.raw.types.UpdateNewStoryReaction>`
            - :obj:`UpdateNotifySettings <pyrogram.raw.types.UpdateNotifySettings>`
            - :obj:`UpdatePaidReactionPrivacy <pyrogram.raw.types.UpdatePaidReactionPrivacy>`
            - :obj:`UpdatePeerBlocked <pyrogram.raw.types.UpdatePeerBlocked>`
            - :obj:`UpdatePeerHistoryTTL <pyrogram.raw.types.UpdatePeerHistoryTTL>`
            - :obj:`UpdatePeerLocated <pyrogram.raw.types.UpdatePeerLocated>`
            - :obj:`UpdatePeerSettings <pyrogram.raw.types.UpdatePeerSettings>`
            - :obj:`UpdatePeerWallpaper <pyrogram.raw.types.UpdatePeerWallpaper>`
            - :obj:`UpdatePendingJoinRequests <pyrogram.raw.types.UpdatePendingJoinRequests>`
            - :obj:`UpdatePhoneCall <pyrogram.raw.types.UpdatePhoneCall>`
            - :obj:`UpdatePhoneCallSignalingData <pyrogram.raw.types.UpdatePhoneCallSignalingData>`
            - :obj:`UpdatePinnedChannelMessages <pyrogram.raw.types.UpdatePinnedChannelMessages>`
            - :obj:`UpdatePinnedDialogs <pyrogram.raw.types.UpdatePinnedDialogs>`
            - :obj:`UpdatePinnedForumTopic <pyrogram.raw.types.UpdatePinnedForumTopic>`
            - :obj:`UpdatePinnedForumTopics <pyrogram.raw.types.UpdatePinnedForumTopics>`
            - :obj:`UpdatePinnedMessages <pyrogram.raw.types.UpdatePinnedMessages>`
            - :obj:`UpdatePinnedSavedDialogs <pyrogram.raw.types.UpdatePinnedSavedDialogs>`
            - :obj:`UpdatePrivacy <pyrogram.raw.types.UpdatePrivacy>`
            - :obj:`UpdatePtsChanged <pyrogram.raw.types.UpdatePtsChanged>`
            - :obj:`UpdateQuickReplies <pyrogram.raw.types.UpdateQuickReplies>`
            - :obj:`UpdateQuickReplyMessage <pyrogram.raw.types.UpdateQuickReplyMessage>`
            - :obj:`UpdateReadChannelDiscussionInbox <pyrogram.raw.types.UpdateReadChannelDiscussionInbox>`
            - :obj:`UpdateReadChannelDiscussionOutbox <pyrogram.raw.types.UpdateReadChannelDiscussionOutbox>`
            - :obj:`UpdateReadChannelInbox <pyrogram.raw.types.UpdateReadChannelInbox>`
            - :obj:`UpdateReadChannelOutbox <pyrogram.raw.types.UpdateReadChannelOutbox>`
            - :obj:`UpdateReadFeaturedEmojiStickers <pyrogram.raw.types.UpdateReadFeaturedEmojiStickers>`
            - :obj:`UpdateReadFeaturedStickers <pyrogram.raw.types.UpdateReadFeaturedStickers>`
            - :obj:`UpdateReadHistoryInbox <pyrogram.raw.types.UpdateReadHistoryInbox>`
            - :obj:`UpdateReadHistoryOutbox <pyrogram.raw.types.UpdateReadHistoryOutbox>`
            - :obj:`UpdateReadMessagesContents <pyrogram.raw.types.UpdateReadMessagesContents>`
            - :obj:`UpdateReadMonoForumInbox <pyrogram.raw.types.UpdateReadMonoForumInbox>`
            - :obj:`UpdateReadMonoForumOutbox <pyrogram.raw.types.UpdateReadMonoForumOutbox>`
            - :obj:`UpdateReadStories <pyrogram.raw.types.UpdateReadStories>`
            - :obj:`UpdateRecentEmojiStatuses <pyrogram.raw.types.UpdateRecentEmojiStatuses>`
            - :obj:`UpdateRecentReactions <pyrogram.raw.types.UpdateRecentReactions>`
            - :obj:`UpdateRecentStickers <pyrogram.raw.types.UpdateRecentStickers>`
            - :obj:`UpdateSavedDialogPinned <pyrogram.raw.types.UpdateSavedDialogPinned>`
            - :obj:`UpdateSavedGifs <pyrogram.raw.types.UpdateSavedGifs>`
            - :obj:`UpdateSavedReactionTags <pyrogram.raw.types.UpdateSavedReactionTags>`
            - :obj:`UpdateSavedRingtones <pyrogram.raw.types.UpdateSavedRingtones>`
            - :obj:`UpdateSentPhoneCode <pyrogram.raw.types.UpdateSentPhoneCode>`
            - :obj:`UpdateSentStoryReaction <pyrogram.raw.types.UpdateSentStoryReaction>`
            - :obj:`UpdateServiceNotification <pyrogram.raw.types.UpdateServiceNotification>`
            - :obj:`UpdateSmsJob <pyrogram.raw.types.UpdateSmsJob>`
            - :obj:`UpdateStarsBalance <pyrogram.raw.types.UpdateStarsBalance>`
            - :obj:`UpdateStarsRevenueStatus <pyrogram.raw.types.UpdateStarsRevenueStatus>`
            - :obj:`UpdateStickerSets <pyrogram.raw.types.UpdateStickerSets>`
            - :obj:`UpdateStickerSetsOrder <pyrogram.raw.types.UpdateStickerSetsOrder>`
            - :obj:`UpdateStoriesStealthMode <pyrogram.raw.types.UpdateStoriesStealthMode>`
            - :obj:`UpdateStory <pyrogram.raw.types.UpdateStory>`
            - :obj:`UpdateStoryID <pyrogram.raw.types.UpdateStoryID>`
            - :obj:`UpdateTheme <pyrogram.raw.types.UpdateTheme>`
            - :obj:`UpdateTranscribedAudio <pyrogram.raw.types.UpdateTranscribedAudio>`
            - :obj:`UpdateUser <pyrogram.raw.types.UpdateUser>`
            - :obj:`UpdateUserEmojiStatus <pyrogram.raw.types.UpdateUserEmojiStatus>`
            - :obj:`UpdateUserName <pyrogram.raw.types.UpdateUserName>`
            - :obj:`UpdateUserPhone <pyrogram.raw.types.UpdateUserPhone>`
            - :obj:`UpdateUserStatus <pyrogram.raw.types.UpdateUserStatus>`
            - :obj:`UpdateUserTyping <pyrogram.raw.types.UpdateUserTyping>`
            - :obj:`UpdateWebPage <pyrogram.raw.types.UpdateWebPage>`
            - :obj:`UpdateWebViewResultSent <pyrogram.raw.types.UpdateWebViewResultSent>`
        """

        QUALNAME = "pyrogram.raw.base.Update"
        __union_types__ = Union[raw.types.UpdateAttachMenuBots, raw.types.UpdateAutoSaveSettings, raw.types.UpdateBotBusinessConnect, raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotChatBoost, raw.types.UpdateBotChatInviteRequester, raw.types.UpdateBotCommands, raw.types.UpdateBotDeleteBusinessMessage, raw.types.UpdateBotEditBusinessMessage, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend, raw.types.UpdateBotMenuButton, raw.types.UpdateBotMessageReaction, raw.types.UpdateBotMessageReactions, raw.types.UpdateBotNewBusinessMessage, raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotPurchasedPaidMedia, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotStopped, raw.types.UpdateBotWebhookJSON, raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateBusinessBotCallbackQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages, raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant, raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping, raw.types.UpdateChannelViewForumAsMessages, raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights, raw.types.UpdateChatParticipant, raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete, raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig, raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages, raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteQuickReply, raw.types.UpdateDeleteQuickReplyMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter, raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned, raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage, raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead, raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers, raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallChainBlocks, raw.types.UpdateGroupCallConnection, raw.types.UpdateGroupCallEncryptedMessage, raw.types.UpdateGroupCallMessage, raw.types.UpdateGroupCallParticipants, raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong, raw.types.UpdateLoginToken, raw.types.UpdateMessageExtendedMedia, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll, raw.types.UpdateMessagePollVote, raw.types.UpdateMessageReactions, raw.types.UpdateMonoForumNoPaidException, raw.types.UpdateMoveStickerSetToTop, raw.types.UpdateNewAuthorization, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage, raw.types.UpdateNewMessage, raw.types.UpdateNewQuickReply, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet, raw.types.UpdateNewStoryReaction, raw.types.UpdateNotifySettings, raw.types.UpdatePaidReactionPrivacy, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerHistoryTTL, raw.types.UpdatePeerLocated, raw.types.UpdatePeerSettings, raw.types.UpdatePeerWallpaper, raw.types.UpdatePendingJoinRequests, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData, raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedForumTopic, raw.types.UpdatePinnedForumTopics, raw.types.UpdatePinnedMessages, raw.types.UpdatePinnedSavedDialogs, raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateQuickReplies, raw.types.UpdateQuickReplyMessage, raw.types.UpdateReadChannelDiscussionInbox, raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox, raw.types.UpdateReadFeaturedEmojiStickers, raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox, raw.types.UpdateReadMessagesContents, raw.types.UpdateReadMonoForumInbox, raw.types.UpdateReadMonoForumOutbox, raw.types.UpdateReadStories, raw.types.UpdateRecentEmojiStatuses, raw.types.UpdateRecentReactions, raw.types.UpdateRecentStickers, raw.types.UpdateSavedDialogPinned, raw.types.UpdateSavedGifs, raw.types.UpdateSavedReactionTags, raw.types.UpdateSavedRingtones, raw.types.UpdateSentPhoneCode, raw.types.UpdateSentStoryReaction, raw.types.UpdateServiceNotification, raw.types.UpdateSmsJob, raw.types.UpdateStarsBalance, raw.types.UpdateStarsRevenueStatus, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder, raw.types.UpdateStoriesStealthMode, raw.types.UpdateStory, raw.types.UpdateStoryID, raw.types.UpdateTheme, raw.types.UpdateTranscribedAudio, raw.types.UpdateUser, raw.types.UpdateUserEmojiStatus, raw.types.UpdateUserName, raw.types.UpdateUserPhone, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping, raw.types.UpdateWebPage, raw.types.UpdateWebViewResultSent]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.live/telegram/base/update")
