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


class InternalServerError(RPCError):
    """Internal Server Error"""
    CODE = 500
    """``int``: RPC Error Code"""
    NAME = __doc__


class AuthKeyUnsynchronized(InternalServerError):
    """Internal error, please repeat the method call."""
    ID = "AUTH_KEY_UNSYNCHRONIZED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthRestart(InternalServerError):
    """Restart the authorization process."""
    ID = "AUTH_RESTART"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthRestartX(InternalServerError):
    """Internal error (debug info {value}), please repeat the method call."""
    ID = "AUTH_RESTART_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallOccupyFailed(InternalServerError):
    """The call failed because the user is already making another call."""
    ID = "CALL_OCCUPY_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CdnUploadTimeout(InternalServerError):
    """A server-side timeout occurred while reuploading the file to the CDN DC."""
    ID = "CDN_UPLOAD_TIMEOUT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatIdGenerateFailed(InternalServerError):
    """Failure while generating the chat ID."""
    ID = "CHAT_ID_GENERATE_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatInvalid(InternalServerError):
    """Invalid chat."""
    ID = "CHAT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptionDeclineAdminFailed(InternalServerError):
    """"""
    ID = "ENCRYPTION_DECLINE_ADMIN_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallAddParticipantsFailed(InternalServerError):
    """"""
    ID = "GROUPCALL_ADD_PARTICIPANTS_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MsgWaitFailed(InternalServerError):
    """A waiting call returned an error."""
    ID = "MSG_WAIT_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NeedDocInvalid(InternalServerError):
    """"""
    ID = "NEED_DOC_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantCallFailed(InternalServerError):
    """"""
    ID = "PARTICIPANT_CALL_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasskeyAuthRestart(InternalServerError):
    """"""
    ID = "PASSKEY_AUTH_RESTART"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PersistentTimestampOutdated(InternalServerError):
    """Channel internal replication issues, try again later (treat this like an RPC_CALL_FAIL)."""
    ID = "PERSISTENT_TIMESTAMP_OUTDATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RandomIdDuplicate(InternalServerError):
    """You provided a random ID that was already used."""
    ID = "RANDOM_ID_DUPLICATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendMediaInvalid(InternalServerError):
    """The specified media is invalid."""
    ID = "SEND_MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SignInFailed(InternalServerError):
    """Failure while signing in."""
    ID = "SIGN_IN_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TranslateReqFailed(InternalServerError):
    """Translation failed, please try again later."""
    ID = "TRANSLATE_REQ_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TranslationTimeout(InternalServerError):
    """A timeout occurred while translating the specified text."""
    ID = "TRANSLATION_TIMEOUT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VolumeMoveInvalid(InternalServerError):
    """"""
    ID = "VOLUME_MOVE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


