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

from typing import Optional

import pyrogram
from pyrogram import raw, types

from ..object import Object


class ComposedMessageWithAI(Object):
    """Contains the result of an AI-composed message.

    Parameters:
        result_text (:obj:`~pyrogram.types.FormattedText`):
            The AI-composed result text.

        diff_text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            The diff between the original text and the result text (for proofreading).
    """

    def __init__(
        self,
        *,
        result_text: "types.FormattedText",
        diff_text: Optional["types.FormattedText"] = None,
    ):
        super().__init__()

        self.result_text = result_text
        self.diff_text = diff_text

    @staticmethod
    def _parse(client: "pyrogram.Client", composed: "raw.types.messages.ComposedMessageWithAI") -> "ComposedMessageWithAI":
        return ComposedMessageWithAI(
            result_text=types.FormattedText._parse(client, composed.result_text),
            diff_text=types.FormattedText._parse(client, composed.diff_text) if composed.diff_text else None,
        )
