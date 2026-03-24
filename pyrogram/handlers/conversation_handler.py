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

from typing import Union

import pyrogram
from pyrogram import utils
from pyrogram.types import Message, CallbackQuery
from .message_handler import MessageHandler
from .callback_query_handler import CallbackQueryHandler
from .handler import Handler


class ConversationHandler(MessageHandler, CallbackQueryHandler):
    """The Conversation handler class."""
    def __init__(self):
        Handler.__init__(self, self.callback)
        self.original_callback = self.callback
        self.waiters = {}

    def register_waiter(self, chat_id, waiter):
        old = self.waiters.get(chat_id)
        if old and not old['future'].done():
            old['future'].cancel()
        self.waiters[chat_id] = waiter

    async def check(self, client: "pyrogram.Client", update: Union[Message, CallbackQuery]):
        if not self.waiters:
            return False

        if isinstance(update, Message) and update.outgoing:
            return False

        try:
            chat_id = update.chat.id if isinstance(update, Message) else update.message.chat.id
        except AttributeError:
            return False

        waiter = self.waiters.get(chat_id)
        if not waiter or not isinstance(update, waiter['update_type']) or waiter['future'].done():
            return False

        filters = waiter.get('filters')
        if callable(filters):
            filtered = await utils.invoke_callable(
                filters, client, update,
                executor=client.executor, loop=client.loop
            )

            if not filtered or waiter['future'].done():
                return False

        waiter['future'].set_result(update)
        return True

    @staticmethod
    async def callback(_, __):
        raise pyrogram.StopPropagation

    def delete_waiter(self, chat_id, future):
        waiter = self.waiters.get(chat_id)
        if waiter and waiter.get('future') == future:
            del self.waiters[chat_id]