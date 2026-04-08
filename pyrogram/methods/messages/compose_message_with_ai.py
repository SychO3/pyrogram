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
from pyrogram import raw, types, utils


class ComposeMessageWithAI:
    async def compose_message_with_ai(
        self: "pyrogram.Client",
        text: str,
        proofread: Optional[bool] = None,
        emojify: Optional[bool] = None,
        translate_to_lang: Optional[str] = None,
        change_tone: Optional[str] = None,
    ) -> "types.ComposedMessageWithAI":
        """Use Telegram's AI to compose, proofread, translate, change tone, or emojify a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            text (``str``):
                The input text to compose or modify with AI.

            proofread (``bool``, *optional*):
                Pass True to proofread the text.

            emojify (``bool``, *optional*):
                Pass True to add emojis to the text.

            translate_to_lang (``str``, *optional*):
                Language code to translate the text to.

            change_tone (``str``, *optional*):
                Tone to change the text to.
                Must be one of "formal", "short", "tribal", "corp", "biblical", "viking", "zen".

        Returns:
            :obj:`~pyrogram.types.ComposedMessageWithAI`: On success, the AI-composed message is returned.

        Example:
            .. code-block:: python

                # Proofread a message
                result = await app.compose_message_with_ai("Helo wrold!", proofread=True)
                print(result.result_text.text)

                # Translate a message
                result = await app.compose_message_with_ai("Hello!", translate_to_lang="ru")
                print(result.result_text.text)

                # Change tone
                result = await app.compose_message_with_ai("Fix this now.", change_tone="formal")
                print(result.result_text.text)
        """
        if not any([proofread, emojify, translate_to_lang, change_tone]):
            raise ValueError(
                "At least one task must be specified: "
                "proofread, emojify, translate_to_lang, or change_tone"
            )

        message, entities = (await utils.parse_text_entities(self, text, None, None)).values()

        r = await self.invoke(
            raw.functions.messages.ComposeMessageWithAI(
                text=raw.types.TextWithEntities(
                    text=message,
                    entities=entities or []
                ),
                proofread=proofread,
                emojify=emojify,
                translate_to_lang=translate_to_lang,
                change_tone=change_tone,
            )
        )

        return types.ComposedMessageWithAI._parse(self, r)
