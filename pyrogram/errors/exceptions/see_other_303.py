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


class SeeOther(RPCError):
    """See Other"""
    CODE = 303
    """``int``: RPC Error Code"""
    NAME = __doc__


class NetworkMigrateX(SeeOther):
    """Your IP address is associated to DC {value}, please re-send the query to that DC."""
    ID = "NETWORK_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneMigrateX(SeeOther):
    """Your phone number is associated to DC {value}, please re-send the query to that DC."""
    ID = "PHONE_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StatsMigrateX(SeeOther):
    """Channel statistics for the specified channel are stored on DC {value}, please re-send the query to that DC."""
    ID = "STATS_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserMigrateX(SeeOther):
    """Your account is associated to DC {value}, please re-send the query to that DC."""
    ID = "USER_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


