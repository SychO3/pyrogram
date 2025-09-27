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

log = logging.getLogger(__name__)


class Connect:
    async def connect(
        self: "pyrogram.Client",
    ) -> bool:
        """
        Connect the client to Telegram servers.

        Returns:
            ``bool``: On success, in case the passed-in session is authorized, True is returned. Otherwise, in case
            the session needs to be authorized, False is returned.

        Raises:
            ConnectionError: In case you try to connect an already connected client.
        """
        if self.is_connected:
            raise ConnectionError("Client is already connected")

        await self.load_session()

        self.session = await self.get_session(
            server_address=await self.storage.server_address(),
            port=await self.storage.port(),
            export_authorization=False,
            temporary=True
        )
        self.is_connected = True

        is_ipv6_session = ":" in await self.storage.server_address()

        if (self.ipv6 and not is_ipv6_session) or (
            not self.ipv6 and is_ipv6_session
        ):
            await self.set_dc(dc_id=await self.storage.dc_id())

        # Optimize endpoint after first connection (triggers selector & logs)
        try:
            dc_id = await self.storage.dc_id()
            best = await self.get_dc_option(dc_id=dc_id, ipv6=self.ipv6)

            cur_ip = await self.storage.server_address()
            cur_port = await self.storage.port()

            if best.ip_address != cur_ip or best.port != cur_port:
                log.info("Optimize endpoint: switching DC%s from %s:%s to %s:%s", dc_id, cur_ip, cur_port, best.ip_address, best.port)
                await self.set_dc(dc_id=dc_id, server_address=best.ip_address, port=best.port)
        except Exception as e:
            log.info("Endpoint optimization failed: %s %s", type(e).__name__, e)

        return bool(await self.storage.user_id())
