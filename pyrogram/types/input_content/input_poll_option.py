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

import os
import re
from typing import BinaryIO, Optional, Union

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileType

from ..object import Object


class InputPollOption(Object):
    """This object contains information about one answer option in a poll to be sent.

    Parameters:
        text (``str`` | :obj:`~pyrogram.enums.FormattedText`, *optional*):
            Option text, 1-100 characters.

        media (:obj:`~pyrogram.types.InputPollOptionMedia` | ``str`` | ``BinaryIO``, *optional*):
            Option media. ``str`` and ``BinaryIO`` values are treated as photo media for backwards compatibility.
    """

    def __init__(
        self,
        *,
        text: Union[str, "types.FormattedText"],
        media: Optional[Union["types.InputPollOptionMedia", str, BinaryIO]] = None,
    ):
        super().__init__()

        self.text = text
        self.media = media

    async def write(self, client: "pyrogram.Client") -> "raw.types.InputPollAnswer":
        if isinstance(self.text, str):
            self.text = types.FormattedText(text=self.text)

        input_media = None

        if self.media is not None:
            if hasattr(self.media, "write"):
                input_media = await self.media.write(client=client)
            elif isinstance(self.media, str):
                if os.path.isfile(self.media):
                    file = await client.save_file(self.media)
                    input_media = raw.types.InputMediaUploadedPhoto(file=file)
                elif re.match("^https?://", self.media):
                    input_media = raw.types.InputMediaPhotoExternal(url=self.media)
                else:
                    input_media = utils.get_input_media_from_file_id(self.media, FileType.PHOTO)
            else:
                file = await client.save_file(self.media)
                input_media = raw.types.InputMediaUploadedPhoto(file=file)

        return raw.types.InputPollAnswer(
            text=await self.text.write(client),
            media=input_media,
        )
