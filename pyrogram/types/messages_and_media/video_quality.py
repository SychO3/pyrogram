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

from datetime import datetime
from typing import List, Optional

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType

from ..object import Object


class VideoQuality(Object):
    """Describes the quality of a video.

    Parameters:
        file_id (``str``):
            Identifier for this file, which can be used to download or reuse the file.

        file_unique_id (``str``):
            Unique identifier for this file, which is supposed to be the same over time and for different accounts.
            Can't be used to download or reuse the file.

        width (``int``):
            Video width.

        height (``int``):
            Video height.

        codec (``str``):
            Codec used to encode the video (e.g. "h264", "h265", "av1").

        duration (``float``, *optional*):
            Duration of the video in seconds.

        file_name (``str``, *optional*):
            Video file name.

        mime_type (``str``, *optional*):
            Mime type of the video file.

        file_size (``int``, *optional*):
            File size in bytes.

        supports_streaming (``bool``, *optional*):
            True, if the video supports streaming.

        nosound (``bool``, *optional*):
            True, if the video has no sound.

        preload_prefix_size (``int``, *optional*):
            Size of the preload prefix in bytes.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the video was uploaded.

        thumbs (List of :obj:`~pyrogram.types.Thumbnail`, *optional*):
            Video thumbnails.
    """
    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        codec: str,
        duration: Optional[float] = None,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        supports_streaming: Optional[bool] = None,
        nosound: Optional[bool] = None,
        preload_prefix_size: Optional[int] = None,
        date: Optional[datetime] = None,
        thumbs: Optional[List["types.Thumbnail"]] = None
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.codec = codec
        self.duration = duration
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.supports_streaming = supports_streaming
        self.nosound = nosound
        self.preload_prefix_size = preload_prefix_size
        self.date = date
        self.thumbs = thumbs

    @staticmethod
    def _parse(
        client,
        doc: "raw.types.Document",
        video_attributes: "raw.types.DocumentAttributeVideo",
        file_name: str = None
    ) -> "VideoQuality":
        return VideoQuality(
            file_id=FileId(
                file_type=FileType.VIDEO,
                dc_id=doc.dc_id,
                media_id=doc.id,
                access_hash=doc.access_hash,
                file_reference=doc.file_reference
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT,
                media_id=doc.id
            ).encode(),
            width=getattr(video_attributes, "w", None),
            height=getattr(video_attributes, "h", None),
            codec=getattr(video_attributes, "video_codec", None),
            duration=video_attributes.duration,
            file_name=file_name,
            mime_type=doc.mime_type,
            file_size=doc.size,
            supports_streaming=video_attributes.supports_streaming,
            nosound=video_attributes.nosound,
            preload_prefix_size=getattr(video_attributes, "preload_prefix_size", None),
            date=utils.timestamp_to_datetime(doc.date),
            thumbs=types.Thumbnail._parse(client, doc),
            client=client
        )
