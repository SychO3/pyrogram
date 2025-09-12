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


class InlineQueryResultGif(InlineQueryResult):
    """Link to an animated GIF file.

    By default, this animated GIF file will be sent by the user with optional caption.
    Alternatively, you can use *input_message_content* to send a message with the specified content instead of the
    animation.

    Parameters:
        gif_url (``str``):
            A valid URL for the GIF file. File size must not exceed 1MB.

        thumb_url (``str``, *optional*):
            URL of the static (JPEG or GIF) or animated (MPEG4) thumbnail for the result.
            Defaults to the value passed in *gif_url*.

        gif_width (``int``, *optional*):
            Width of the GIF.

        gif_height (``int``, *optional*):
            Height of the GIF.

        gif_duration (``int``, *optional*):
            Duration of the GIF in seconds.

        id (``str``, *optional*):
            Unique identifier for this result, 1-64 bytes.
            Defaults to a randomly generated UUID4.

        title (``str``, *optional*):
            Title for the result.

        caption (``str``, *optional*):
            Caption of the GIF file to be sent, 0-1024 characters.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
            An InlineKeyboardMarkup object.

        input_message_content (:obj:`~pyrogram.types.InputMessageContent`):
            Content of the message to be sent instead of the GIF animation.
    """

    def __init__(
        self,
        gif_url: str,
        thumb_url: str = None,
        gif_width: int = 0,
        gif_height: int = 0,
        gif_duration: int = 0,
        id: str = None,
        title: str = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        reply_markup: "types.InlineKeyboardMarkup" = None,
        input_message_content: "types.InputMessageContent" = None
    ):
        super().__init__("gif", id, input_message_content, reply_markup)

        self.gif_url = gif_url
        self.thumb_url = thumb_url
        self.gif_width = gif_width
        self.gif_height = gif_height
        self.gif_duration = gif_duration
        self.title = title
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content

    async def write(self, client: "pyrogram.Client"):
        gif = raw.types.InputWebDocument(
            url=self.gif_url,
            size=0,
            mime_type="image/gif",
            attributes=[
                raw.types.DocumentAttributeImageSize(
                    w=self.gif_width,
                    h=self.gif_height
                ),
                raw.types.DocumentAttributeAnimated()
            ]
        )

        if self.thumb_url is None:
            thumb = gif
        else:
            thumb = raw.types.InputWebDocument(
                url=self.thumb_url,
                size=0,
                mime_type="image/jpeg",
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
            content=gif,
            send_message=(
                await self.input_message_content.write(client, self.reply_markup)
                if self.input_message_content
                else raw.types.InputBotInlineMessageMediaAuto(
                    reply_markup=await self.reply_markup.write(client) if self.reply_markup else None,
                    message=message,
                    entities=entities
                )
            )
        )