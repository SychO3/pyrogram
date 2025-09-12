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

from typing import Optional, List

import pyrogram
from pyrogram import raw, types, utils, enums
from .inline_query_result import InlineQueryResult


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video without sound).

    By default, this animated MPEG-4 file will be sent by the user with optional caption.
    Alternatively, you can use input_message_content to send a message with the specified content instead of the animation.

    Parameters:
        mpeg4_url (``str``):
            A valid URL for the MPEG4 file.

        thumb_url (``str``, *optional*):
            URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail for the result

        thumbnail_mime_type (``str``, *optional*):
            MIME type of the thumbnail, must be one of “image/jpeg”, “image/gif”, or “video/mp4”.
            Defaults to “image/jpeg”.

        mpeg4_width (``int``, *optional*):
            Video width.

        mpeg4_height (``int``, *optional*):
            Video height.

        mpeg4_duration (``int``, *optional*):
            Video duration in seconds.

        id (``str``, *optional*):
            Unique identifier for this result, 1-64 bytes.
            Defaults to a randomly generated UUID4.

        title (``str``, *optional*):
            Title for the result.

        caption (``str``, *optional*):
            Caption of the MPEG-4 file to be sent, 0-1024 characters.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (``bool``, *optional*):
            If true, the caption will be shown above the media; otherwise, it will be shown below the media.
            Defaults to False.

        reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
            An InlineKeyboardMarkup object.

        input_message_content (:obj:`~pyrogram.types.InputMessageContent`):
            Content of the message to be sent instead of the video.
    """

    def __init__(
        self,
        mpeg4_url: str,
        thumb_url: str = None,
        thumbnail_mime_type: str = "image/jpeg",
        mpeg4_width: int = 0,
        mpeg4_height: int = 0,
        mpeg4_duration: int = 0,
        id: str = None,
        title: str = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        show_caption_above_media: bool = False,
        reply_markup: "types.InlineKeyboardMarkup" = None,
        input_message_content: "types.InputMessageContent" = None
    ):
        super().__init__("gif", id, input_message_content, reply_markup)

        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url
        self.thumbnail_mime_type = thumbnail_mime_type
        self.mpeg4_width = mpeg4_width
        self.mpeg4_height = mpeg4_height
        self.mpeg4_duration = mpeg4_duration
        self.title = title
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content

    async def write(self, client: "pyrogram.Client"):
        video = raw.types.InputWebDocument(
            url=self.mpeg4_url,
            size=0,
            mime_type="video/mp4",
            attributes=[
                raw.types.DocumentAttributeVideo(
                    w=self.mpeg4_width,
                    h=self.mpeg4_height,
                    duration=self.mpeg4_duration,
                    supports_streaming=True
                ),
                raw.types.DocumentAttributeAnimated()
            ]
        )

        if self.thumb_url is None:
            thumb = video
        else:
            thumb = raw.types.InputWebDocument(
                url=self.thumb_url,
                size=0,
                mime_type=self.thumbnail_mime_type or "image/jpeg",
                attributes=[]
            )

        message, entities = (await utils.parse_text_entities(
            client, self.caption, self.parse_mode, self.caption_entities
        )).values()

        return raw.types.InputBotInlineResult(
            id=self.id,
            type=self.type,
            title=self.title,
            thumb=thumb,
            content=video,
            send_message=(
                await self.input_message_content.write(client, self.reply_markup)
                if self.input_message_content
                else raw.types.InputBotInlineMessageMediaAuto(
                    reply_markup=await self.reply_markup.write(client) if self.reply_markup else None,
                    message=message,
                    entities=entities,
                    invert_media=self.show_caption_above_media
                )
            )
        )