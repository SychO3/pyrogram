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

import pyrogram

from pyrogram import utils
from pyrogram.errors import ListenerStopped
from pyrogram.types import Listener
from pyrogram.utils import PyromodConfig

class StopListener:
    async def stop_listener(
        self: "pyrogram.Client",
        listener: Listener
    ):
        """Stops a listener, calling stopped_handler if applicable or raising ListenerStopped if throw_exceptions is True.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            listener (:obj:`~pyrogram.types.Listener`):
                The listener to remove.

        Raises:
            ListenerStopped: If throw_exceptions is True.
        """
        self.remove_listener(listener)

        if listener.future and listener.future.done():
            return

        if callable(PyromodConfig.stopped_handler):
            await utils.invoke_callable(
                PyromodConfig.stopped_handler, listener,
                executor=self.executor, loop=self.loop
            )

        if listener.future and not listener.future.done():
            if PyromodConfig.throw_exceptions:
                listener.future.set_exception(ListenerStopped())
            else:
                listener.future.cancel()