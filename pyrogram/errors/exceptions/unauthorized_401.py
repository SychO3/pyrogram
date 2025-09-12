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


class Unauthorized(RPCError):
    """Unauthorized"""
    CODE = 401
    """``int``: RPC Error Code"""
    NAME = __doc__


class AuthKeyInvalid(Unauthorized):
    """The specified auth key is invalid."""
    ID = "AUTH_KEY_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthKeyPermEmpty(Unauthorized):
    """The method is unavailable for temporary authorization keys, not bound to a permanent authorization key."""
    ID = "AUTH_KEY_PERM_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthKeyUnregistered(Unauthorized):
    """The specified authorization key is not registered in the system (for example, a PFS temporary key has expired)."""
    ID = "AUTH_KEY_UNREGISTERED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SessionExpired(Unauthorized):
    """The session has expired."""
    ID = "SESSION_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SessionPasswordNeeded(Unauthorized):
    """2FA is enabled, use a password to login."""
    ID = "SESSION_PASSWORD_NEEDED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SessionRevoked(Unauthorized):
    """The session was revoked by the user."""
    ID = "SESSION_REVOKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserDeactivated(Unauthorized):
    """The current account was deleted by the user."""
    ID = "USER_DEACTIVATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserDeactivatedBan(Unauthorized):
    """The current account was deleted and banned by Telegram's antispam system."""
    ID = "USER_DEACTIVATED_BAN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


