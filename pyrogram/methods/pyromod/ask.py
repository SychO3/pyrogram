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

import asyncio
from typing import TYPE_CHECKING
import pyrogram

from pyrogram import utils
from pyrogram.filters import Filter
from pyrogram.errors import ListenerTimeout
from pyrogram.types import Identifier, Listener
from pyrogram.utils import PyromodConfig
from typing import List, Optional, Union

if TYPE_CHECKING:
    from pyrogram import types as _types
    from pyrogram.types.pyromod import SentMessage as _SentMessage

    class _MessageWithPrompt(_types.Message):
        sent_message: Optional[_SentMessage]

    class _CallbackQueryWithPrompt(_types.CallbackQuery):
        sent_message: Optional[_SentMessage]

class Ask:
    async def ask(
        self: "pyrogram.Client",
        chat_id: Union[Union[int, str], List[Union[int, str]]],
        text: str,
        filters: Optional[Filter] = None,
        listener_type: "pyrogram.enums.ListenerTypes" = pyrogram.enums.ListenerTypes.MESSAGE,
        timeout: Optional[int] = None,
        unallowed_click_alert: bool = True,
        user_id: Union[Union[int, str], List[Union[int, str]]] = None,
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        *args,
        **kwargs,
    ) -> "Union[_MessageWithPrompt, _CallbackQueryWithPrompt]":
        """Send a message then listen for a message, callback query, etc.

        Message:

        .. include:: /_includes/usable-by/users-bots.rst

        CallbackQuery:

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | Iterable of ``int`` | Iterable of ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Note: when sending a prompt (text provided), this must resolve to exactly one id.

            text (``str``):
                Text of the message to be sent.

            user_id (``int`` | ``str`` | Iterable of ``int`` | Iterable of ``str``, *optional*):
                The user ID to listen for.

            filters (:obj:`~pyrogram.filters`, *optional*):
                A filter to check the incoming message against.

            listener_type (:obj:`~pyrogram.enums.ListenerTypes`, *optional*):
                The type of listener to listen for.
                Default to Message.

            timeout (``int``, *optional*):
                The maximum amount of time to wait for a message.

            unallowed_click_alert (``bool``, *optional*):
                Whether to alert the user if they click a button that doesn’t match the filters.
                Default to True.

            message_id (``int``, *optional*):
                The message ID to listen for.

            inline_message_id (``str``, *optional*):
                The inline message ID to listen for.

        Returns:
            :obj:`~pyrogram.types.Message` | :obj:`~pyrogram.types.CallbackQuery`: On success, a message/callbackquery is returned.

        Example:
            .. code-block:: python

                await app.ask(chat_id, "Tell me your name:")
        """
        # Register listener BEFORE sending prompt to avoid losing fast replies
        pattern = Identifier(
            from_user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

        future = self.loop.create_future()

        listener = Listener(
            future=future,
            filters=filters,
            unallowed_click_alert=unallowed_click_alert,
            identifier=pattern,
            listener_type=listener_type,
        )

        future.add_done_callback(lambda _future: self.remove_listener(listener))
        self.listeners[listener_type].append(listener)

        sent_message = None
        try:
            if text and isinstance(text, str):
                if isinstance(chat_id, list):
                    if len(chat_id) != 1:
                        # Clean up listener before raising
                        self.remove_listener(listener)
                        raise ValueError("ask() requires exactly one chat_id when sending a prompt")
                    chat_to_ask = chat_id[0]
                else:
                    chat_to_ask = chat_id
                sent_message = await self.send_message(chat_to_ask, text, *args, **kwargs)

            try:
                response = await asyncio.wait_for(future, timeout)
            except asyncio.TimeoutError:
                if callable(PyromodConfig.timeout_handler):
                    await utils.invoke_callable(
                        PyromodConfig.timeout_handler, pattern, listener, timeout,
                        executor=self.executor, loop=self.loop
                    )
                elif PyromodConfig.throw_exceptions:
                    try:
                        self.remove_listener(listener)
                    except Exception:
                        pass
                    raise ListenerTimeout(timeout)

                try:
                    self.remove_listener(listener)
                except Exception:
                    pass
                response = None

            if response:
                response.sent_message = sent_message
            return response
        except Exception:
            # Ensure listener is removed on errors during sending or handling
            try:
                self.remove_listener(listener)
            except Exception:
                pass
            raise