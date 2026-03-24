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
from typing import Callable, Tuple

import pyrogram

from pyrogram import utils
from pyrogram.utils import PyromodConfig
from pyrogram.types import CallbackQuery, Identifier, Listener

from .handler import Handler


class CallbackQueryHandler(Handler):
    """The CallbackQuery handler class. Used to handle callback queries coming from inline buttons.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_callback_query` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new CallbackQuery arrives. It takes *(client, callback_query)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of callback queries to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        callback_query (:obj:`~pyrogram.types.CallbackQuery`):
            The received callback query.
    """

    def __init__(self, callback: Callable, filters=None):
        self.original_callback = callback
        super().__init__(self.resolve_future_or_callback, filters)

    def compose_data_identifier(self, query: CallbackQuery):
        """
        Composes an Identifier object from a CallbackQuery object.

        :param query: The CallbackQuery object to compose of.
        :return: An Identifier object.
        """
        from_user = query.from_user
        from_user_id = from_user.id if from_user else None
        from_user_username = from_user.username if from_user else None

        chat_id = None
        message_id = None

        if query.message:
            message_id = getattr(
                query.message, "id", getattr(query.message, "message_id", None)
            )

            if query.message.chat:
                chat_id = [query.message.chat.id, query.message.chat.username]

        return Identifier(
            message_id=message_id,
            chat_id=chat_id,
            from_user_id=[from_user_id, from_user_username],
            inline_message_id=query.inline_message_id,
        )

    async def check_if_has_matching_listener(
        self, client: "pyrogram.Client", query: CallbackQuery
    ) -> Tuple[bool, Listener]:
        """
        Checks if the CallbackQuery object has a matching listener.

        :param client: The Client object to check with.
        :param query: The CallbackQuery object to check with.
        :return: A tuple of a boolean and a Listener object. The boolean indicates whether
        the found listener has filters and its filters matches with the CallbackQuery object.
        The Listener object is the matching listener.
        """
        data = self.compose_data_identifier(query)

        listener = client.get_listener_matching_with_data(
            data, pyrogram.enums.ListenerTypes.CALLBACK_QUERY
        )

        listener_does_match = False

        if listener:
            filters = listener.filters
            if callable(filters):
                listener_does_match = await utils.invoke_callable(
                    filters, client, query,
                    executor=client.executor, loop=client.loop
                )
            else:
                listener_does_match = True

        return listener_does_match, listener

    async def check(self, client: "pyrogram.Client", query: CallbackQuery):
        """
        Checks if the CallbackQuery object has a matching listener or handler.

        :param client: The Client object to check with.
        :param query: The CallbackQuery object to check with.
        :return: A boolean indicating whether the CallbackQuery object has a matching listener or the handler
        filter matches.
        """
        listener_does_match, listener = await self.check_if_has_matching_listener(
            client, query
        )

        query._matched_listener = listener if listener_does_match else None

        if callable(self.filters):
            handler_does_match = await utils.invoke_callable(
                self.filters, client, query,
                executor=client.executor, loop=client.loop
            )
        else:
            handler_does_match = True

        if PyromodConfig.unallowed_click_alert and listener:
            data = self.compose_data_identifier(query)
            permissive_identifier = Identifier(
                chat_id=data.chat_id,
                message_id=data.message_id,
                inline_message_id=data.inline_message_id,
                from_user_id=None,
            )

            if (
                permissive_identifier.matches(data)
                and not listener_does_match
                and listener.unallowed_click_alert
            ):
                alert = (
                    listener.unallowed_click_alert
                    if isinstance(listener.unallowed_click_alert, str)
                    else PyromodConfig.unallowed_click_alert_text
                )
                await query.answer(alert)
                return False

        return listener_does_match or handler_does_match

    async def resolve_future_or_callback(
        self, client: "pyrogram.Client", query: CallbackQuery, *args
    ):
        """
        Resolves the future or calls the callback of the listener. Will call the original handler if no listener.

        :param client: The Client object to resolve or call with.
        :param query: The CallbackQuery object to resolve or call with.
        :param args: The arguments to call the callback with.
        :return: None
        """
        listener = getattr(query, '_matched_listener', None)
        listener_does_match = listener is not None

        if not listener_does_match:
            listener_does_match, listener = await self.check_if_has_matching_listener(client, query)

        if listener and listener_does_match:
            client.remove_listener(listener)

            if listener.future and not listener.future.done():
                try:
                    listener.future.set_result(query)
                except asyncio.CancelledError:
                    # Future cancelled during shutdown; stop propagation silently
                    raise pyrogram.StopPropagation

                raise pyrogram.StopPropagation
            elif listener.callback:
                try:
                    await utils.invoke_callable(listener.callback, client, query, *args)
                except asyncio.CancelledError:
                    raise pyrogram.StopPropagation

                raise pyrogram.StopPropagation
            else:
                raise ValueError("Listener must have either a future or a callback")
        else:
            await self.original_callback(client, query, *args)