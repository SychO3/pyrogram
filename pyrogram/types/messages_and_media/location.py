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

from pyrogram import raw
from ..object import Object


class Location(Object):
    """A point on the map.

    Parameters:
        longitude (``float``):
            Longitude as defined by sender.

        latitude (``float``):
            Latitude as defined by sender.

        horizontal_accuracy (``float``, *optional*):
            The radius of uncertainty for the location, measured in meters; 0-1500.

        live_period (``int``, *optional*):
            Time relative to the message sending date, during which the location can be updated; in seconds.
            For active live locations only.

        heading (``int``, *optional*):
            The direction in which user is moving, in degrees; 1-360.
            For active live locations only.

        proximity_alert_radius (``int``, *optional*):
            The maximum distance for proximity alerts about approaching another chat member, in meters.
            For sent live locations only.

        address (``str``, *optional*):
            Address of the location. For business locations only.

        stopped (``bool``, *optional*):
            True if the live location has been stopped. For live locations only.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        longitude: float,
        latitude: float,
        horizontal_accuracy: float = None,
        live_period: int = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        address: str = None,
        stopped: bool = None
    ):
        super().__init__(client)

        self.longitude = longitude
        self.latitude = latitude
        self.horizontal_accuracy = horizontal_accuracy
        self.live_period = live_period
        self.heading = heading
        self.proximity_alert_radius = proximity_alert_radius
        self.address = address
        self.stopped = stopped

    @staticmethod
    def _parse(client, geo_point: Union["raw.types.GeoPoint", "raw.types.BusinessLocation", "raw.types.InputGeoPoint", "raw.types.InputMediaGeoLive"]) -> "Location":
        if isinstance(geo_point, raw.types.GeoPoint):
            return Location(
                longitude=geo_point.long,
                latitude=geo_point.lat,
                horizontal_accuracy=getattr(geo_point, "accuracy_radius", None),
                client=client
            )

        if isinstance(geo_point, raw.types.BusinessLocation):
            return Location(
                longitude=getattr(geo_point.geo_point, "long", None),
                latitude=getattr(geo_point.geo_point, "lat", None),
                horizontal_accuracy=getattr(geo_point.geo_point, "accuracy_radius", None),
                address=geo_point.address,
                client=client
            )

        if isinstance(geo_point, raw.types.InputGeoPoint):
            return Location(
                longitude=geo_point.long,
                latitude=geo_point.lat,
                horizontal_accuracy=getattr(geo_point, "accuracy_radius", None),
                client=client
            )

        if isinstance(geo_point, raw.types.InputMediaGeoLive):
            return Location(
                longitude=getattr(geo_point.geo_point, "long", None),
                latitude=getattr(geo_point.geo_point, "lat", None),
                horizontal_accuracy=getattr(geo_point.geo_point, "accuracy_radius", None),
                heading=getattr(geo_point, "heading", None),
                live_period=getattr(geo_point, "period", None),
                proximity_alert_radius=getattr(geo_point, "proximity_notification_radius", None),
                stopped=getattr(geo_point, "stopped", None),
                client=client
            )
