from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Vehicle')


@_attrs_define
class Vehicle:
    """Attributes:
    trip_id (None | str | Unset):
    direction_id (int | Unset):
    direction (None | str | Unset):
    location_time (int | Unset):
    route_id (None | str | Unset):
    terminal (None | str | Unset):
    latitude (float | Unset):
    longitude (float | Unset):
    bearing (float | Unset):
    odometer (float | Unset):
    speed (float | Unset):
    """

    trip_id: None | str | Unset = UNSET
    direction_id: int | Unset = UNSET
    direction: None | str | Unset = UNSET
    location_time: int | Unset = UNSET
    route_id: None | str | Unset = UNSET
    terminal: None | str | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    bearing: float | Unset = UNSET
    odometer: float | Unset = UNSET
    speed: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        trip_id: None | str | Unset
        if isinstance(self.trip_id, Unset):
            trip_id = UNSET
        else:
            trip_id = self.trip_id

        direction_id = self.direction_id

        direction: None | str | Unset
        if isinstance(self.direction, Unset):
            direction = UNSET
        else:
            direction = self.direction

        location_time = self.location_time

        route_id: None | str | Unset
        if isinstance(self.route_id, Unset):
            route_id = UNSET
        else:
            route_id = self.route_id

        terminal: None | str | Unset
        if isinstance(self.terminal, Unset):
            terminal = UNSET
        else:
            terminal = self.terminal

        latitude = self.latitude

        longitude = self.longitude

        bearing = self.bearing

        odometer = self.odometer

        speed = self.speed

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if trip_id is not UNSET:
            field_dict['trip_id'] = trip_id
        if direction_id is not UNSET:
            field_dict['direction_id'] = direction_id
        if direction is not UNSET:
            field_dict['direction'] = direction
        if location_time is not UNSET:
            field_dict['location_time'] = location_time
        if route_id is not UNSET:
            field_dict['route_id'] = route_id
        if terminal is not UNSET:
            field_dict['terminal'] = terminal
        if latitude is not UNSET:
            field_dict['latitude'] = latitude
        if longitude is not UNSET:
            field_dict['longitude'] = longitude
        if bearing is not UNSET:
            field_dict['bearing'] = bearing
        if odometer is not UNSET:
            field_dict['odometer'] = odometer
        if speed is not UNSET:
            field_dict['speed'] = speed

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_trip_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        trip_id = _parse_trip_id(d.pop('trip_id', UNSET))

        direction_id = d.pop('direction_id', UNSET)

        def _parse_direction(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        direction = _parse_direction(d.pop('direction', UNSET))

        location_time = d.pop('location_time', UNSET)

        def _parse_route_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        route_id = _parse_route_id(d.pop('route_id', UNSET))

        def _parse_terminal(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        terminal = _parse_terminal(d.pop('terminal', UNSET))

        latitude = d.pop('latitude', UNSET)

        longitude = d.pop('longitude', UNSET)

        bearing = d.pop('bearing', UNSET)

        odometer = d.pop('odometer', UNSET)

        speed = d.pop('speed', UNSET)

        vehicle = cls(
            trip_id=trip_id,
            direction_id=direction_id,
            direction=direction,
            location_time=location_time,
            route_id=route_id,
            terminal=terminal,
            latitude=latitude,
            longitude=longitude,
            bearing=bearing,
            odometer=odometer,
            speed=speed,
        )

        return vehicle
