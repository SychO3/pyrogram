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
    MessageAction = Union[raw.types.MessageActionBoostApply, raw.types.MessageActionBotAllowed, raw.types.MessageActionChannelCreate, raw.types.MessageActionChannelMigrateFrom, raw.types.MessageActionChatAddUser, raw.types.MessageActionChatCreate, raw.types.MessageActionChatDeletePhoto, raw.types.MessageActionChatDeleteUser, raw.types.MessageActionChatEditPhoto, raw.types.MessageActionChatEditTitle, raw.types.MessageActionChatJoinedByLink, raw.types.MessageActionChatJoinedByRequest, raw.types.MessageActionChatMigrateTo, raw.types.MessageActionConferenceCall, raw.types.MessageActionContactSignUp, raw.types.MessageActionCustomAction, raw.types.MessageActionEmpty, raw.types.MessageActionGameScore, raw.types.MessageActionGeoProximityReached, raw.types.MessageActionGiftCode, raw.types.MessageActionGiftPremium, raw.types.MessageActionGiftStars, raw.types.MessageActionGiftTon, raw.types.MessageActionGiveawayLaunch, raw.types.MessageActionGiveawayResults, raw.types.MessageActionGroupCall, raw.types.MessageActionGroupCallScheduled, raw.types.MessageActionHistoryClear, raw.types.MessageActionInviteToGroupCall, raw.types.MessageActionPaidMessagesPrice, raw.types.MessageActionPaidMessagesRefunded, raw.types.MessageActionPaymentRefunded, raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe, raw.types.MessageActionPhoneCall, raw.types.MessageActionPinMessage, raw.types.MessageActionPrizeStars, raw.types.MessageActionRequestedPeer, raw.types.MessageActionRequestedPeerSentMe, raw.types.MessageActionScreenshotTaken, raw.types.MessageActionSecureValuesSent, raw.types.MessageActionSecureValuesSentMe, raw.types.MessageActionSetChatTheme, raw.types.MessageActionSetChatWallPaper, raw.types.MessageActionSetMessagesTTL, raw.types.MessageActionStarGift, raw.types.MessageActionStarGiftUnique, raw.types.MessageActionSuggestBirthday, raw.types.MessageActionSuggestProfilePhoto, raw.types.MessageActionSuggestedPostApproval, raw.types.MessageActionSuggestedPostRefund, raw.types.MessageActionSuggestedPostSuccess, raw.types.MessageActionTodoAppendTasks, raw.types.MessageActionTodoCompletions, raw.types.MessageActionTopicCreate, raw.types.MessageActionTopicEdit, raw.types.MessageActionWebViewDataSent, raw.types.MessageActionWebViewDataSentMe]
else:
    # noinspection PyRedeclaration
    class MessageAction(metaclass=BaseTypeMeta):  # type: ignore
        """This base type has 58 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageActionBoostApply <pyrogram.raw.types.MessageActionBoostApply>`
            - :obj:`MessageActionBotAllowed <pyrogram.raw.types.MessageActionBotAllowed>`
            - :obj:`MessageActionChannelCreate <pyrogram.raw.types.MessageActionChannelCreate>`
            - :obj:`MessageActionChannelMigrateFrom <pyrogram.raw.types.MessageActionChannelMigrateFrom>`
            - :obj:`MessageActionChatAddUser <pyrogram.raw.types.MessageActionChatAddUser>`
            - :obj:`MessageActionChatCreate <pyrogram.raw.types.MessageActionChatCreate>`
            - :obj:`MessageActionChatDeletePhoto <pyrogram.raw.types.MessageActionChatDeletePhoto>`
            - :obj:`MessageActionChatDeleteUser <pyrogram.raw.types.MessageActionChatDeleteUser>`
            - :obj:`MessageActionChatEditPhoto <pyrogram.raw.types.MessageActionChatEditPhoto>`
            - :obj:`MessageActionChatEditTitle <pyrogram.raw.types.MessageActionChatEditTitle>`
            - :obj:`MessageActionChatJoinedByLink <pyrogram.raw.types.MessageActionChatJoinedByLink>`
            - :obj:`MessageActionChatJoinedByRequest <pyrogram.raw.types.MessageActionChatJoinedByRequest>`
            - :obj:`MessageActionChatMigrateTo <pyrogram.raw.types.MessageActionChatMigrateTo>`
            - :obj:`MessageActionConferenceCall <pyrogram.raw.types.MessageActionConferenceCall>`
            - :obj:`MessageActionContactSignUp <pyrogram.raw.types.MessageActionContactSignUp>`
            - :obj:`MessageActionCustomAction <pyrogram.raw.types.MessageActionCustomAction>`
            - :obj:`MessageActionEmpty <pyrogram.raw.types.MessageActionEmpty>`
            - :obj:`MessageActionGameScore <pyrogram.raw.types.MessageActionGameScore>`
            - :obj:`MessageActionGeoProximityReached <pyrogram.raw.types.MessageActionGeoProximityReached>`
            - :obj:`MessageActionGiftCode <pyrogram.raw.types.MessageActionGiftCode>`
            - :obj:`MessageActionGiftPremium <pyrogram.raw.types.MessageActionGiftPremium>`
            - :obj:`MessageActionGiftStars <pyrogram.raw.types.MessageActionGiftStars>`
            - :obj:`MessageActionGiftTon <pyrogram.raw.types.MessageActionGiftTon>`
            - :obj:`MessageActionGiveawayLaunch <pyrogram.raw.types.MessageActionGiveawayLaunch>`
            - :obj:`MessageActionGiveawayResults <pyrogram.raw.types.MessageActionGiveawayResults>`
            - :obj:`MessageActionGroupCall <pyrogram.raw.types.MessageActionGroupCall>`
            - :obj:`MessageActionGroupCallScheduled <pyrogram.raw.types.MessageActionGroupCallScheduled>`
            - :obj:`MessageActionHistoryClear <pyrogram.raw.types.MessageActionHistoryClear>`
            - :obj:`MessageActionInviteToGroupCall <pyrogram.raw.types.MessageActionInviteToGroupCall>`
            - :obj:`MessageActionPaidMessagesPrice <pyrogram.raw.types.MessageActionPaidMessagesPrice>`
            - :obj:`MessageActionPaidMessagesRefunded <pyrogram.raw.types.MessageActionPaidMessagesRefunded>`
            - :obj:`MessageActionPaymentRefunded <pyrogram.raw.types.MessageActionPaymentRefunded>`
            - :obj:`MessageActionPaymentSent <pyrogram.raw.types.MessageActionPaymentSent>`
            - :obj:`MessageActionPaymentSentMe <pyrogram.raw.types.MessageActionPaymentSentMe>`
            - :obj:`MessageActionPhoneCall <pyrogram.raw.types.MessageActionPhoneCall>`
            - :obj:`MessageActionPinMessage <pyrogram.raw.types.MessageActionPinMessage>`
            - :obj:`MessageActionPrizeStars <pyrogram.raw.types.MessageActionPrizeStars>`
            - :obj:`MessageActionRequestedPeer <pyrogram.raw.types.MessageActionRequestedPeer>`
            - :obj:`MessageActionRequestedPeerSentMe <pyrogram.raw.types.MessageActionRequestedPeerSentMe>`
            - :obj:`MessageActionScreenshotTaken <pyrogram.raw.types.MessageActionScreenshotTaken>`
            - :obj:`MessageActionSecureValuesSent <pyrogram.raw.types.MessageActionSecureValuesSent>`
            - :obj:`MessageActionSecureValuesSentMe <pyrogram.raw.types.MessageActionSecureValuesSentMe>`
            - :obj:`MessageActionSetChatTheme <pyrogram.raw.types.MessageActionSetChatTheme>`
            - :obj:`MessageActionSetChatWallPaper <pyrogram.raw.types.MessageActionSetChatWallPaper>`
            - :obj:`MessageActionSetMessagesTTL <pyrogram.raw.types.MessageActionSetMessagesTTL>`
            - :obj:`MessageActionStarGift <pyrogram.raw.types.MessageActionStarGift>`
            - :obj:`MessageActionStarGiftUnique <pyrogram.raw.types.MessageActionStarGiftUnique>`
            - :obj:`MessageActionSuggestBirthday <pyrogram.raw.types.MessageActionSuggestBirthday>`
            - :obj:`MessageActionSuggestProfilePhoto <pyrogram.raw.types.MessageActionSuggestProfilePhoto>`
            - :obj:`MessageActionSuggestedPostApproval <pyrogram.raw.types.MessageActionSuggestedPostApproval>`
            - :obj:`MessageActionSuggestedPostRefund <pyrogram.raw.types.MessageActionSuggestedPostRefund>`
            - :obj:`MessageActionSuggestedPostSuccess <pyrogram.raw.types.MessageActionSuggestedPostSuccess>`
            - :obj:`MessageActionTodoAppendTasks <pyrogram.raw.types.MessageActionTodoAppendTasks>`
            - :obj:`MessageActionTodoCompletions <pyrogram.raw.types.MessageActionTodoCompletions>`
            - :obj:`MessageActionTopicCreate <pyrogram.raw.types.MessageActionTopicCreate>`
            - :obj:`MessageActionTopicEdit <pyrogram.raw.types.MessageActionTopicEdit>`
            - :obj:`MessageActionWebViewDataSent <pyrogram.raw.types.MessageActionWebViewDataSent>`
            - :obj:`MessageActionWebViewDataSentMe <pyrogram.raw.types.MessageActionWebViewDataSentMe>`
        """

        QUALNAME = "pyrogram.raw.base.MessageAction"
        __union_types__ = Union[raw.types.MessageActionBoostApply, raw.types.MessageActionBotAllowed, raw.types.MessageActionChannelCreate, raw.types.MessageActionChannelMigrateFrom, raw.types.MessageActionChatAddUser, raw.types.MessageActionChatCreate, raw.types.MessageActionChatDeletePhoto, raw.types.MessageActionChatDeleteUser, raw.types.MessageActionChatEditPhoto, raw.types.MessageActionChatEditTitle, raw.types.MessageActionChatJoinedByLink, raw.types.MessageActionChatJoinedByRequest, raw.types.MessageActionChatMigrateTo, raw.types.MessageActionConferenceCall, raw.types.MessageActionContactSignUp, raw.types.MessageActionCustomAction, raw.types.MessageActionEmpty, raw.types.MessageActionGameScore, raw.types.MessageActionGeoProximityReached, raw.types.MessageActionGiftCode, raw.types.MessageActionGiftPremium, raw.types.MessageActionGiftStars, raw.types.MessageActionGiftTon, raw.types.MessageActionGiveawayLaunch, raw.types.MessageActionGiveawayResults, raw.types.MessageActionGroupCall, raw.types.MessageActionGroupCallScheduled, raw.types.MessageActionHistoryClear, raw.types.MessageActionInviteToGroupCall, raw.types.MessageActionPaidMessagesPrice, raw.types.MessageActionPaidMessagesRefunded, raw.types.MessageActionPaymentRefunded, raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe, raw.types.MessageActionPhoneCall, raw.types.MessageActionPinMessage, raw.types.MessageActionPrizeStars, raw.types.MessageActionRequestedPeer, raw.types.MessageActionRequestedPeerSentMe, raw.types.MessageActionScreenshotTaken, raw.types.MessageActionSecureValuesSent, raw.types.MessageActionSecureValuesSentMe, raw.types.MessageActionSetChatTheme, raw.types.MessageActionSetChatWallPaper, raw.types.MessageActionSetMessagesTTL, raw.types.MessageActionStarGift, raw.types.MessageActionStarGiftUnique, raw.types.MessageActionSuggestBirthday, raw.types.MessageActionSuggestProfilePhoto, raw.types.MessageActionSuggestedPostApproval, raw.types.MessageActionSuggestedPostRefund, raw.types.MessageActionSuggestedPostSuccess, raw.types.MessageActionTodoAppendTasks, raw.types.MessageActionTodoCompletions, raw.types.MessageActionTopicCreate, raw.types.MessageActionTopicEdit, raw.types.MessageActionWebViewDataSent, raw.types.MessageActionWebViewDataSentMe]

        def __init__(self):
            raise TypeError("Base types can only be used for type checking purposes: "
                            "you tried to use a base type instance as argument, "
                            "but you need to instantiate one of its constructors instead. "
                            "More info: https://docs.kurigram.live/telegram/base/message-action")
