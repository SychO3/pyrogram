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

from typing import Union, List

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils


class GetGameHighScores:
    async def get_game_high_scores(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        chat_id: Union[int, str],
        message_id: int = None,
        inline_message_id: str = None,
    ) -> List["types.GameHighScore"]:
        """Use this method to get data for high score tables.
        Will return the score of the specified user and several of their neighbors in a game.

        .. note::
            This method will currently return scores for the target user,
            plus two of their closest neighbors on each side.
            Will also return the top three users if the user and their neighbors are not among them.
            Please note that this behavior is subject to change.


        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                Required if inline_message_id is not specified.

            message_id (``int``, *optional*):
                Identifier of the sent message.
                Required if inline_message_id is not specified.

            inline_message_id (``str``, *optional*):
                Identifier of the inline message
                Required if chat_id and message_id are not specified.

        Returns:
            List of :obj:`~pyrogram.types.GameHighScore`: On success.

        Example:
            .. code-block:: python

                scores = await app.get_game_high_scores(user_id, chat_id, message_id)
                print(scores)
        """
        # Convert user identifier to InputUser (not InputPeer), as required by raw layer
        _user_peer = await self.resolve_peer(user_id)
        if isinstance(_user_peer, raw.types.InputPeerSelf):
            _input_user = raw.types.InputUserSelf()
        elif isinstance(_user_peer, raw.types.InputPeerUser):
            _input_user = raw.types.InputUser(user_id=_user_peer.user_id, access_hash=_user_peer.access_hash)
        elif isinstance(_user_peer, raw.types.InputPeerUserFromMessage):
            _input_user = raw.types.InputUserFromMessage(peer=_user_peer.peer, msg_id=_user_peer.msg_id, user_id=_user_peer.user_id)
        else:
            _input_user = None

        if _input_user is None:
            raise ValueError("user_id must be an integer, a username or a phone number of a user")

        if inline_message_id:
            inline_id = utils.unpack_inline_message_id(inline_message_id)

            r = await self.invoke(
                raw.functions.messages.GetInlineGameHighScores(
                    id=inline_id,
                    user_id=_input_user
                )
            )
        else:
            r = await self.invoke(
                raw.functions.messages.GetGameHighScores(
                    peer=await self.resolve_peer(chat_id),
                    id=message_id,
                    user_id=_input_user
                )
            )

        return types.List(types.GameHighScore._parse(self, score, r.users) for score in r.scores)
