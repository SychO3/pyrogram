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

from typing import Union

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils


class SetGameScore:
    async def set_game_score(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        score: int,
        force: bool = None,
        disable_edit_message: bool = None,
        chat_id: Union[int, str] = None,
        message_id: int = None,
        inline_message_id: str = None,
    ) -> Union["types.Message", bool]:
        """Use this method to set the score of the specified user in a game message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            score (``int``):
                New score, must be non-negative.

            force (``bool``, *optional*):
                Pass True, if the high score is allowed to decrease.
                This can be useful when fixing mistakes or banning cheaters.
                Default is False.

            disable_edit_message (``bool``, *optional*):
                Pass True, if the game message should not be automatically edited to include the current scoreboard.
                Default is False.

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
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the message was sent by the bot, the edited
            message is returned, True otherwise.

        Example:
            .. code-block:: python

                # Set new score
                await app.set_game_score(user_id, 1000)

                # Force set new score
                await app.set_game_score(user_id, 25, force=True)
        """

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
                raw.functions.messages.SetInlineGameScore(
                    id=inline_id,
                    user_id=_input_user,
                    score=score,
                    force=force or None,
                    edit_message=not disable_edit_message or None,
                )
            )
            return bool(r)
        else:
            r = await self.invoke(
                raw.functions.messages.SetGameScore(
                    peer=await self.resolve_peer(chat_id),
                    score=score,
                    id=message_id,
                    user_id=_input_user,
                    force=force or None,
                    edit_message=not disable_edit_message or None
                )
            )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateEditMessage,
                              raw.types.UpdateEditChannelMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats}
                )

        return True
