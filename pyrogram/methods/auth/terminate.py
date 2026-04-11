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

import logging

import pyrogram
from pyrogram import raw, utils

log = logging.getLogger(__name__)


class Terminate:
    async def terminate(
        self: "pyrogram.Client",
        clear_handlers: bool = True
    ):
        """Terminate the client by shutting down workers.

        This method does the opposite of :meth:`~pyrogram.Client.initialize`.
        It will stop the dispatcher and shut down updates and download workers.

        Parameters:
            clear_handlers (``bool``, *optional*):
                Clear the already existing handlers on restart the client.
                Default to True.

        Raises:
            ConnectionError: In case you try to terminate a client that is already terminated.
        """
        if not self.is_initialized:
            raise ConnectionError("Client is already terminated")

        if self.takeout_id:
            await self.invoke(raw.functions.account.FinishTakeoutSession())
            log.info("Takeout session %s finished", self.takeout_id)

        # Cancel conversation waiters and listeners
        try:
            conv_handler = self.dispatcher._conversation_handlers.get(0)
            if conv_handler:
                waiters = getattr(conv_handler, "waiters", {}) or {}
                for chat_id, waiter in list(waiters.items()):
                    future = waiter.get("future")
                    if future and not future.done():
                        try:
                            future.cancel()
                        except Exception:
                            pass
                waiters.clear()

            listeners_map = getattr(self, "listeners", {}) or {}
            for _lt, lst in list(listeners_map.items()):
                for listener in list(lst):
                    try:
                        self.remove_listener(listener)
                        if getattr(listener, "future", None) and not listener.future.done():
                            try:
                                listener.future.cancel()
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass

        if callable(self.stop_handler):
            try:
                await utils.invoke_callable(self.stop_handler, self)
            except Exception as e:
                log.exception("stop_handler raised: %s", e)

        # Save update state and storage
        await self._update_state.save_to_storage(self.storage)
        await self.storage.save()

        if not self.no_updates:
            await self.dispatcher.stop()

            if clear_handlers:
                self.dispatcher.unregister_bot(0)

        for media_session in self.media_sessions.values():
            await media_session.stop()

        self.media_sessions.clear()

        for aux_session in self.sessions.values():
            await aux_session.stop()

        self.sessions.clear()
        self._session_futures.clear()

        self.updates_watchdog_event.set()

        if self.updates_watchdog_task is not None:
            await self.updates_watchdog_task

        self.updates_watchdog_event.clear()

        if hasattr(self, "executor") and self.executor:
            self.executor.shutdown(wait=False)

        self.is_initialized = False
