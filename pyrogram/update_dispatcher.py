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

from __future__ import annotations

import asyncio
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

import pyrogram
from pyrogram import utils
from pyrogram.handlers import (
    BusinessConnectionHandler,
    BusinessMessageHandler,
    CallbackQueryHandler,
    ChatBoostHandler,
    ChatJoinRequestHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    ConversationHandler,
    DeletedBusinessMessagesHandler,
    DeletedMessagesHandler,
    EditedBusinessMessageHandler,
    EditedMessageHandler,
    ErrorHandler,
    Handler,
    InlineQueryHandler,
    ManagedBotUpdatedHandler,
    MessageHandler,
    MessageReactionCountHandler,
    MessageReactionHandler,
    PollHandler,
    PreCheckoutQueryHandler,
    PurchasedPaidMediaHandler,
    RawUpdateHandler,
    ShippingQueryHandler,
    StoryHandler,
    UserStatusHandler,
)
from pyrogram.raw.types import (
    UpdateBotBusinessConnect,
    UpdateBotCallbackQuery,
    UpdateBotChatBoost,
    UpdateBotChatInviteRequester,
    UpdateBotDeleteBusinessMessage,
    UpdateBotEditBusinessMessage,
    UpdateBotInlineQuery,
    UpdateBotInlineSend,
    UpdateBotMessageReaction,
    UpdateBotMessageReactions,
    UpdateBotNewBusinessMessage,
    UpdateBotPrecheckoutQuery,
    UpdateBotPurchasedPaidMedia,
    UpdateBotShippingQuery,
    UpdateBusinessBotCallbackQuery,
    UpdateChannelParticipant,
    UpdateChatParticipant,
    UpdateDeleteChannelMessages,
    UpdateDeleteMessages,
    UpdateEditChannelMessage,
    UpdateEditMessage,
    UpdateInlineBotCallbackQuery,
    UpdateManagedBot,
    UpdateMessagePoll,
    UpdateMessagePollVote,
    UpdateNewChannelMessage,
    UpdateNewMessage,
    UpdateNewScheduledMessage,
    UpdateStory,
    UpdateUserStatus,
)

if TYPE_CHECKING:
    from pyrogram.runtime import Runtime

log = logging.getLogger(__name__)


# --- Data-driven parser registry ---
# Maps update type -> (parser_function, handler_type)
# Parser functions take (client, update, users, chats) and return parsed object

async def _parse_message(client, update, users, chats):
    connection_id = getattr(update, "connection_id", None)
    return await pyrogram.types.Message._parse(
        client, update.message, users, chats,
        is_scheduled=isinstance(update, UpdateNewScheduledMessage),
        replies=0 if connection_id else 1,
        business_connection_id=connection_id,
        raw_reply_to_message=getattr(update, "reply_to_message", None),
    )

async def _parse_edited_message(client, update, users, chats):
    connection_id = getattr(update, "connection_id", None)
    return await pyrogram.types.Message._parse(
        client, update.message, users, chats,
        is_scheduled=False,
        replies=0 if connection_id else 1,
        business_connection_id=connection_id,
        raw_reply_to_message=getattr(update, "reply_to_message", None),
    )

async def _parse_deleted_messages(client, update, users, chats):
    return utils.parse_deleted_messages(client, update, users, chats)

async def _parse_callback_query(client, update, users, chats):
    return await pyrogram.types.CallbackQuery._parse(client, update, users, chats)

async def _parse_user_status(client, update, users, chats):
    return pyrogram.types.User._parse_user_status(client, update)

async def _parse_inline_query(client, update, users, chats):
    return pyrogram.types.InlineQuery._parse(client, update, users)

async def _parse_poll(client, update, users, chats):
    return pyrogram.types.Poll._parse_update(client, update, users, chats)

async def _parse_chosen_inline_result(client, update, users, chats):
    return pyrogram.types.ChosenInlineResult._parse(client, update, users)

async def _parse_chat_member_updated(client, update, users, chats):
    return pyrogram.types.ChatMemberUpdated._parse(client, update, users, chats)

async def _parse_chat_join_request(client, update, users, chats):
    return pyrogram.types.ChatJoinRequest._parse(client, update, users, chats)

async def _parse_story(client, update, users, chats):
    return await pyrogram.types.Story._parse(client, update.story, update.peer, users, chats)

async def _parse_pre_checkout_query(client, update, users, chats):
    return await pyrogram.types.PreCheckoutQuery._parse(client, update, users)

async def _parse_shipping_query(client, update, users, chats):
    return await pyrogram.types.ShippingQuery._parse(client, update, users)

async def _parse_message_reaction(client, update, users, chats):
    return pyrogram.types.MessageReactionUpdated._parse(client, update, users, chats)

async def _parse_message_reaction_count(client, update, users, chats):
    return pyrogram.types.MessageReactionCountUpdated._parse(client, update, users, chats)

async def _parse_chat_boost(client, update, users, chats):
    return pyrogram.types.ChatBoostUpdated._parse(client, update, users, chats)

async def _parse_purchased_paid_media(client, update, users, chats):
    return pyrogram.types.PurchasedPaidMedia._parse(client, update, users)

async def _parse_business_connection(client, update, users, chats):
    return pyrogram.types.BusinessConnection._parse(client, update, users)

async def _parse_business_message(client, update, users, chats):
    return await _parse_message(client, update, users, chats)

async def _parse_edited_business_message(client, update, users, chats):
    return await _parse_message(client, update, users, chats)

async def _parse_deleted_business_messages(client, update, users, chats):
    return utils.parse_deleted_messages(client, update, users, chats)

async def _parse_managed_bot(client, update, users, chats):
    return await pyrogram.types.ManagedBotUpdated._parse(client, update, users)


# Map update type -> (parser_fn, handler_type)
PARSER_MAP: Dict[type, Tuple[Callable, Type[Handler]]] = {}

_REGISTRATIONS = [
    ((UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage), _parse_message, MessageHandler),
    ((UpdateEditMessage, UpdateEditChannelMessage), _parse_edited_message, EditedMessageHandler),
    ((UpdateDeleteMessages, UpdateDeleteChannelMessages), _parse_deleted_messages, DeletedMessagesHandler),
    ((UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery, UpdateBusinessBotCallbackQuery), _parse_callback_query, CallbackQueryHandler),
    ((UpdateUserStatus,), _parse_user_status, UserStatusHandler),
    ((UpdateBotInlineQuery,), _parse_inline_query, InlineQueryHandler),
    ((UpdateMessagePoll, UpdateMessagePollVote), _parse_poll, PollHandler),
    ((UpdateBotInlineSend,), _parse_chosen_inline_result, ChosenInlineResultHandler),
    ((UpdateChatParticipant, UpdateChannelParticipant), _parse_chat_member_updated, ChatMemberUpdatedHandler),
    ((UpdateBotChatInviteRequester,), _parse_chat_join_request, ChatJoinRequestHandler),
    ((UpdateStory,), _parse_story, StoryHandler),
    ((UpdateBotPrecheckoutQuery,), _parse_pre_checkout_query, PreCheckoutQueryHandler),
    ((UpdateBotShippingQuery,), _parse_shipping_query, ShippingQueryHandler),
    ((UpdateBotMessageReaction,), _parse_message_reaction, MessageReactionHandler),
    ((UpdateBotMessageReactions,), _parse_message_reaction_count, MessageReactionCountHandler),
    ((UpdateBotChatBoost,), _parse_chat_boost, ChatBoostHandler),
    ((UpdateBotPurchasedPaidMedia,), _parse_purchased_paid_media, PurchasedPaidMediaHandler),
    ((UpdateBotBusinessConnect,), _parse_business_connection, BusinessConnectionHandler),
    ((UpdateBotNewBusinessMessage,), _parse_business_message, BusinessMessageHandler),
    ((UpdateBotEditBusinessMessage,), _parse_edited_business_message, EditedBusinessMessageHandler),
    ((UpdateBotDeleteBusinessMessage,), _parse_deleted_business_messages, DeletedBusinessMessagesHandler),
    ((UpdateManagedBot,), _parse_managed_bot, ManagedBotUpdatedHandler),
]

for _update_types, _parser, _handler_type in _REGISTRATIONS:
    for _update_type in _update_types:
        PARSER_MAP[_update_type] = (_parser, _handler_type)


class UpdateDispatcher:
    """Centralized update dispatcher for multi-tenant runtime.

    Routes updates to per-bot handler groups with per-bot ordering locks.
    Uses a shared worker pool and data-driven parser registry.
    """

    def __init__(self, runtime: "Runtime", worker_count: int = 32):
        self._runtime = runtime
        self._worker_count = worker_count

        self._queue: asyncio.Queue = asyncio.Queue(maxsize=50000)
        self._worker_tasks: List[asyncio.Task] = []

        # Per-bot handler groups: bot_id -> OrderedDict[group_id, list[Handler]]
        self._handler_groups: Dict[int, OrderedDict] = {}
        # Per-bot conversation handlers
        self._conversation_handlers: Dict[int, ConversationHandler] = {}
        # Per-bot ordering locks: updates for the same bot are serialized
        self._bot_locks: Dict[int, asyncio.Lock] = {}

    async def start(self) -> None:
        loop = asyncio.get_event_loop()
        for _ in range(self._worker_count):
            self._worker_tasks.append(loop.create_task(self._worker()))
        log.info("UpdateDispatcher started with %d workers", self._worker_count)

    async def stop(self) -> None:
        for _ in range(self._worker_count):
            self._queue.put_nowait(None)
        for task in self._worker_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._worker_tasks.clear()
        log.info("UpdateDispatcher stopped")

    def register_bot(self, bot_id: int) -> None:
        if bot_id not in self._handler_groups:
            conv = ConversationHandler()
            self._conversation_handlers[bot_id] = conv
            groups = OrderedDict()
            groups[0] = [conv]
            self._handler_groups[bot_id] = groups

    def unregister_bot(self, bot_id: int) -> None:
        self._handler_groups.pop(bot_id, None)
        self._conversation_handlers.pop(bot_id, None)
        self._bot_locks.pop(bot_id, None)

    def add_handler(self, bot_id: int, handler: Handler, group: int) -> None:
        self.register_bot(bot_id)
        groups = self._handler_groups[bot_id]
        new_groups = OrderedDict(groups)
        if group not in new_groups:
            new_groups[group] = []
            new_groups = OrderedDict(sorted(new_groups.items()))
        new_groups[group] = list(new_groups[group]) + [handler]
        self._handler_groups[bot_id] = new_groups

    def remove_handler(self, bot_id: int, handler: Handler, group: int) -> None:
        groups = self._handler_groups.get(bot_id)
        if not groups or group not in groups:
            return
        new_groups = OrderedDict(groups)
        handlers = list(new_groups.get(group, []))
        try:
            handlers.remove(handler)
        except ValueError:
            return
        if handlers:
            new_groups[group] = handlers
        else:
            del new_groups[group]
        self._handler_groups[bot_id] = new_groups

    async def dispatch(self, bot_id: int, raw_update: Any) -> None:
        try:
            self._queue.put_nowait((bot_id, raw_update))
        except asyncio.QueueFull:
            log.warning("Update queue full, dropping update for bot %d", bot_id)

    async def _worker(self) -> None:
        while True:
            item = await self._queue.get()
            if item is None:
                return

            bot_id, raw_update = item
            try:
                lock = self._bot_locks.setdefault(bot_id, asyncio.Lock())
                async with lock:
                    await self._process_update(bot_id, raw_update)
            except Exception:
                log.exception("Unhandled exception in update worker for bot %d", bot_id)

    async def _process_update(self, bot_id: int, raw_update: Any) -> None:
        bot = self._runtime.bots.get(bot_id)
        if bot is None:
            return

        groups = self._handler_groups.get(bot_id)
        if not groups:
            return

        # Parse the update
        update_type = type(raw_update)
        parser_entry = PARSER_MAP.get(update_type)

        # For raw updates that come as (update, users, chats) tuples
        if isinstance(raw_update, tuple):
            update, users, chats = raw_update
            update_type = type(update)
            parser_entry = PARSER_MAP.get(update_type)
        else:
            update = raw_update
            users = {}
            chats = {}

        parsed_update = None
        handler_type = type(None)

        if parser_entry is not None:
            parser_fn, handler_type = parser_entry
            try:
                parsed_update = await parser_fn(bot, update, users, chats)
            except Exception:
                log.exception("Parser failed for %s (bot %d)", update_type.__name__, bot_id)
                return

        # Iterate handler groups
        for group in groups.values():
            for handler in group:
                if isinstance(handler, ErrorHandler):
                    continue

                args = None

                if isinstance(handler, handler_type) and parsed_update is not None:
                    try:
                        if await handler.check(bot, parsed_update):
                            args = (parsed_update,)
                    except Exception:
                        log.exception("Handler check failed")
                        continue
                elif isinstance(handler, RawUpdateHandler):
                    try:
                        if await handler.check(bot, update):
                            args = (update, users, chats)
                    except Exception:
                        log.exception("Raw handler check failed")
                        continue

                if args is None:
                    continue

                try:
                    await utils.invoke_callable(
                        handler.callback, bot, *args,
                        executor=bot.executor, loop=bot.loop,
                    )
                except asyncio.CancelledError:
                    raise
                except pyrogram.StopPropagation:
                    return
                except pyrogram.ContinuePropagation:
                    continue
                except Exception as exc:
                    await self._handle_error(bot_id, bot, exc, handler, update, users, chats)

                break

    async def _handle_error(
        self, bot_id: int, bot: Any, exc: Exception,
        update_handler: Handler, update: Any, users: dict, chats: dict,
    ) -> None:
        groups = self._handler_groups.get(bot_id, {})
        handled = False

        try:
            for group in groups.values():
                for handler in group:
                    if not isinstance(handler, ErrorHandler):
                        continue
                    if not isinstance(exc, handler.exceptions):
                        continue
                    try:
                        await utils.invoke_callable(
                            handler.callback, bot, exc, update_handler, update, users, chats,
                            executor=bot.executor, loop=bot.loop,
                        )
                    except pyrogram.StopPropagation:
                        handled = True
                        raise
                    except pyrogram.ContinuePropagation:
                        handled = True
                        continue
                    except Exception:
                        log.exception("Error handler raised:")
                    else:
                        handled = True
                    break
        except pyrogram.StopPropagation:
            pass
        finally:
            if not handled:
                log.error(
                    "Unhandled exception in %s for bot %d:",
                    type(update_handler).__name__, bot_id,
                    exc_info=(type(exc), exc, exc.__traceback__),
                )
