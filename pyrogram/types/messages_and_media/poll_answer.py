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

from typing import Dict, List, Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object
from ..update import Update


class PollAnswer(Object, Update):
    """Represents an answer of a user in a non-anonymous poll.

    Parameters:
        poll_id (``str``):
            Unique poll identifier.

        user (:obj:`~pyrogram.types.User`, *optional*):
            The user that changed the answer to the poll, if the voter isn't anonymous.

        voter_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The chat that changed the answer to the poll, if the voter is anonymous.

        option_persistent_ids (List of ``str``):
            Persistent identifiers of the chosen options.
            May be empty if the user retracted their vote.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        poll_id: str,
        user: Optional["types.User"] = None,
        voter_chat: Optional["types.Chat"] = None,
        option_persistent_ids: List[str],
    ):
        super().__init__(client)

        self.poll_id = poll_id
        self.user = user
        self.voter_chat = voter_chat
        self.option_persistent_ids = option_persistent_ids

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        update: "raw.types.UpdateMessagePollVote",
        users: Dict[int, "raw.types.User"],
        chats: Dict[int, "raw.types.Chat"],
    ) -> "PollAnswer":
        peer_id = utils.get_raw_peer_id(update.peer)

        user = None
        voter_chat = None

        if isinstance(update.peer, raw.types.PeerUser):
            user = types.User._parse(client, users.get(peer_id))
        else:
            voter_chat = types.Chat._parse_chat(client, chats.get(peer_id))

        return PollAnswer(
            poll_id=str(update.poll_id),
            user=user,
            voter_chat=voter_chat,
            option_persistent_ids=[option.decode() for option in update.options],
            client=client,
        )
