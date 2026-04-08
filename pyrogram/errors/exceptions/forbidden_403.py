# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from ..rpc_error import RPCError


class Forbidden(RPCError):
    """Forbidden"""
    CODE = 403
    """``int``: RPC Error Code"""
    NAME = __doc__


class AccessDenied(Forbidden):
    """"""
    ID = "ACCESS_DENIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AllowPaymentRequiredX(Forbidden):
    """This peer charges {value} [Telegram Stars](https://core.telegram.org/api/stars) per message, but the `allow_paid_stars` was not set or its value is smaller than {value}."""
    ID = "ALLOW_PAYMENT_REQUIRED_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AnonymousReactionsDisabled(Forbidden):
    """Sorry, anonymous administrators cannot leave reactions or participate in polls."""
    ID = "ANONYMOUS_REACTIONS_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotAccessForbidden(Forbidden):
    """The specified method *can* be used over a [business connection](https://core.telegram.org/api/bots/connected-business-bots) for some operations, but the specified query attempted an operation that is not allowed over a business connection."""
    ID = "BOT_ACCESS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotVerifierForbidden(Forbidden):
    """This bot cannot assign [verification icons](https://core.telegram.org/api/bots/verification)."""
    ID = "BOT_VERIFIER_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BroadcastForbidden(Forbidden):
    """Channel poll voters and reactions cannot be fetched to prevent deanonymization."""
    ID = "BROADCAST_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelPublicGroupNa(Forbidden):
    """channel/supergroup not available."""
    ID = "CHANNEL_PUBLIC_GROUP_NA"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatActionForbidden(Forbidden):
    """You cannot execute this action."""
    ID = "CHAT_ACTION_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAdminInviteRequired(Forbidden):
    """You do not have the rights to do this."""
    ID = "CHAT_ADMIN_INVITE_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAdminRequired(Forbidden):
    """You must be an admin in this chat to do this."""
    ID = "CHAT_ADMIN_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatForbidden(Forbidden):
    """This chat is not available to the current user."""
    ID = "CHAT_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatGuestSendForbidden(Forbidden):
    """You join the discussion group before commenting, see [here &raquo;](https://core.telegram.org/api/discussion#requiring-users-to-join-the-group) for more info."""
    ID = "CHAT_GUEST_SEND_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendAudiosForbidden(Forbidden):
    """You can't send audio messages in this chat."""
    ID = "CHAT_SEND_AUDIOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendDocsForbidden(Forbidden):
    """You can't send documents in this chat."""
    ID = "CHAT_SEND_DOCS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendGameForbidden(Forbidden):
    """You can't send a game to this chat."""
    ID = "CHAT_SEND_GAME_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendGifsForbidden(Forbidden):
    """You can't send gifs in this chat."""
    ID = "CHAT_SEND_GIFS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendInlineForbidden(Forbidden):
    """You can't send inline messages in this group."""
    ID = "CHAT_SEND_INLINE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendMediaForbidden(Forbidden):
    """You can't send media in this chat."""
    ID = "CHAT_SEND_MEDIA_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPhotosForbidden(Forbidden):
    """You can't send photos in this chat."""
    ID = "CHAT_SEND_PHOTOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPlainForbidden(Forbidden):
    """You can't send non-media (text) messages in this chat."""
    ID = "CHAT_SEND_PLAIN_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPollForbidden(Forbidden):
    """You can't send polls in this chat."""
    ID = "CHAT_SEND_POLL_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendRoundvideosForbidden(Forbidden):
    """You can't send round videos to this chat."""
    ID = "CHAT_SEND_ROUNDVIDEOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendStickersForbidden(Forbidden):
    """You can't send stickers in this chat."""
    ID = "CHAT_SEND_STICKERS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendVideosForbidden(Forbidden):
    """You can't send videos in this chat."""
    ID = "CHAT_SEND_VIDEOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendVoicesForbidden(Forbidden):
    """You can't send voice recordings in this chat."""
    ID = "CHAT_SEND_VOICES_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendWebpageForbidden(Forbidden):
    """You can't send webpage previews to this chat."""
    ID = "CHAT_SEND_WEBPAGE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatTypeInvalid(Forbidden):
    """The specified user type is invalid."""
    ID = "CHAT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatWriteForbidden(Forbidden):
    """You can't write in this chat."""
    ID = "CHAT_WRITE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EditBotInviteForbidden(Forbidden):
    """Normal users can't edit invites that were created by bots."""
    ID = "EDIT_BOT_INVITE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallAlreadyStarted(Forbidden):
    """The groupcall has already started, you can join directly using [phone.joinGroupCall](https://core.telegram.org/method/phone.joinGroupCall)."""
    ID = "GROUPCALL_ALREADY_STARTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallForbidden(Forbidden):
    """The group call has already ended."""
    ID = "GROUPCALL_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InlineBotRequired(Forbidden):
    """Only the inline bot can edit message."""
    ID = "INLINE_BOT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageAuthorRequired(Forbidden):
    """Message author required."""
    ID = "MESSAGE_AUTHOR_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageDeleteForbidden(Forbidden):
    """You can't delete one of the messages you tried to delete, most likely because it is a service message."""
    ID = "MESSAGE_DELETE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NotEligible(Forbidden):
    """The current user is not eligible to join the Peer-to-Peer Login Program."""
    ID = "NOT_ELIGIBLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantJoinMissing(Forbidden):
    """Trying to enable a presentation, when the user hasn't joined the Video Chat with [phone.joinGroupCall](https://core.telegram.org/method/phone.joinGroupCall)."""
    ID = "PARTICIPANT_JOIN_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PeerIdInvalid(Forbidden):
    """The provided peer id is invalid."""
    ID = "PEER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollVoteRequired(Forbidden):
    """Cast a vote in the poll before calling this method."""
    ID = "POLL_VOTE_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumAccountRequired(Forbidden):
    """A premium account is required to execute this action."""
    ID = "PREMIUM_ACCOUNT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyPremiumRequired(Forbidden):
    """You need a [Telegram Premium subscription](https://core.telegram.org/api/premium) to send a message to this user."""
    ID = "PRIVACY_PREMIUM_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PublicChannelMissing(Forbidden):
    """You can only export group call invite links for public chats or channels."""
    ID = "PUBLIC_CHANNEL_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RightForbidden(Forbidden):
    """Your admin rights do not allow you to do this."""
    ID = "RIGHT_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SensitiveChangeForbidden(Forbidden):
    """You can't change your sensitive content settings."""
    ID = "SENSITIVE_CHANGE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutRequired(Forbidden):
    """A [takeout](https://core.telegram.org/api/takeout) session needs to be initialized first, [see here &raquo; for more info](https://core.telegram.org/api/takeout)."""
    ID = "TAKEOUT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserChannelsTooMuch(Forbidden):
    """One of the users you tried to add is already in too many channels/supergroups."""
    ID = "USER_CHANNELS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserDeleted(Forbidden):
    """You can't send this secret message because the other participant deleted their account."""
    ID = "USER_DELETED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserInvalid(Forbidden):
    """Invalid user provided."""
    ID = "USER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserIsBlocked(Forbidden):
    """You were blocked by this user."""
    ID = "USER_IS_BLOCKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserNotMutualContact(Forbidden):
    """The provided user is not a mutual contact."""
    ID = "USER_NOT_MUTUAL_CONTACT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserNotParticipant(Forbidden):
    """You're not a member of this supergroup/channel."""
    ID = "USER_NOT_PARTICIPANT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserPermissionDenied(Forbidden):
    """The user hasn't granted or has revoked the bot's access to change their emoji status using [bots.toggleUserEmojiStatusPermission](https://core.telegram.org/method/bots.toggleUserEmojiStatusPermission)."""
    ID = "USER_PERMISSION_DENIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserPrivacyRestricted(Forbidden):
    """The user's privacy settings do not allow you to do this."""
    ID = "USER_PRIVACY_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserRestricted(Forbidden):
    """You're spamreported, you can't create channels or chats."""
    ID = "USER_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VoiceMessagesForbidden(Forbidden):
    """This user's privacy settings forbid you from sending voice messages."""
    ID = "VOICE_MESSAGES_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class YourPrivacyRestricted(Forbidden):
    """You cannot fetch the read date of this message because you have disallowed other users to do so for *your* messages; to fix, allow other users to see *your* exact last online date OR purchase a [Telegram Premium](https://core.telegram.org/api/premium) subscription."""
    ID = "YOUR_PRIVACY_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


