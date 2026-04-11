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

from typing import List

import pyrogram
from pyrogram import raw, types

from ..object import Object


class UserProfileAudios(Object):
    """Contains a list of user profile audios.

    Parameters:
        total_count (``int``):
            Total number of profile audios the target user has.

        audios (List of :obj:`~pyrogram.types.Audio`):
            Requested profile audios.
    """
    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        total_count: int,
        audios: List["types.Audio"]
    ):
        super().__init__(client)

        self.total_count = total_count
        self.audios = audios

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        saved_music: "raw.types.users.SavedMusic"
    ) -> "UserProfileAudios":
        audios = []

        for doc in saved_music.documents:
            attributes = {type(i): i for i in doc.attributes}

            if raw.types.DocumentAttributeAudio in attributes:
                audios.append(
                    types.Audio._parse(
                        client,
                        doc,
                        attributes[raw.types.DocumentAttributeAudio],
                        getattr(
                            attributes.get(raw.types.DocumentAttributeFilename, None),
                            "file_name",
                            None,
                        ),
                    )
                )

        return UserProfileAudios(
            total_count=saved_music.count,
            audios=types.List(audios),
            client=client
        )
