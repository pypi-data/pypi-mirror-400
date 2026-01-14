from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Departure')


@_attrs_define
class Departure:
    """Attributes:
    actual (bool | Unset):
    trip_id (None | str | Unset):
    stop_id (int | Unset):
    departure_text (None | str | Unset):
    departure_time (int | Unset):
    description (None | str | Unset):
    gate (None | str | Unset):
    route_id (None | str | Unset):
    route_short_name (None | str | Unset):
    direction_id (int | Unset):
    direction_text (None | str | Unset):
    terminal (None | str | Unset):
    agency_id (int | Unset):
    schedule_relationship (None | str | Unset):
    """

    actual: bool | Unset = UNSET
    trip_id: None | str | Unset = UNSET
    stop_id: int | Unset = UNSET
    departure_text: None | str | Unset = UNSET
    departure_time: int | Unset = UNSET
    description: None | str | Unset = UNSET
    gate: None | str | Unset = UNSET
    route_id: None | str | Unset = UNSET
    route_short_name: None | str | Unset = UNSET
    direction_id: int | Unset = UNSET
    direction_text: None | str | Unset = UNSET
    terminal: None | str | Unset = UNSET
    agency_id: int | Unset = UNSET
    schedule_relationship: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        actual = self.actual

        trip_id: None | str | Unset
        if isinstance(self.trip_id, Unset):
            trip_id = UNSET
        else:
            trip_id = self.trip_id

        stop_id = self.stop_id

        departure_text: None | str | Unset
        if isinstance(self.departure_text, Unset):
            departure_text = UNSET
        else:
            departure_text = self.departure_text

        departure_time = self.departure_time

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        gate: None | str | Unset
        if isinstance(self.gate, Unset):
            gate = UNSET
        else:
            gate = self.gate

        route_id: None | str | Unset
        if isinstance(self.route_id, Unset):
            route_id = UNSET
        else:
            route_id = self.route_id

        route_short_name: None | str | Unset
        if isinstance(self.route_short_name, Unset):
            route_short_name = UNSET
        else:
            route_short_name = self.route_short_name

        direction_id = self.direction_id

        direction_text: None | str | Unset
        if isinstance(self.direction_text, Unset):
            direction_text = UNSET
        else:
            direction_text = self.direction_text

        terminal: None | str | Unset
        if isinstance(self.terminal, Unset):
            terminal = UNSET
        else:
            terminal = self.terminal

        agency_id = self.agency_id

        schedule_relationship: None | str | Unset
        if isinstance(self.schedule_relationship, Unset):
            schedule_relationship = UNSET
        else:
            schedule_relationship = self.schedule_relationship

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if actual is not UNSET:
            field_dict['actual'] = actual
        if trip_id is not UNSET:
            field_dict['trip_id'] = trip_id
        if stop_id is not UNSET:
            field_dict['stop_id'] = stop_id
        if departure_text is not UNSET:
            field_dict['departure_text'] = departure_text
        if departure_time is not UNSET:
            field_dict['departure_time'] = departure_time
        if description is not UNSET:
            field_dict['description'] = description
        if gate is not UNSET:
            field_dict['gate'] = gate
        if route_id is not UNSET:
            field_dict['route_id'] = route_id
        if route_short_name is not UNSET:
            field_dict['route_short_name'] = route_short_name
        if direction_id is not UNSET:
            field_dict['direction_id'] = direction_id
        if direction_text is not UNSET:
            field_dict['direction_text'] = direction_text
        if terminal is not UNSET:
            field_dict['terminal'] = terminal
        if agency_id is not UNSET:
            field_dict['agency_id'] = agency_id
        if schedule_relationship is not UNSET:
            field_dict['schedule_relationship'] = schedule_relationship

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        actual = d.pop('actual', UNSET)

        def _parse_trip_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        trip_id = _parse_trip_id(d.pop('trip_id', UNSET))

        stop_id = d.pop('stop_id', UNSET)

        def _parse_departure_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        departure_text = _parse_departure_text(d.pop('departure_text', UNSET))

        departure_time = d.pop('departure_time', UNSET)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        description = _parse_description(d.pop('description', UNSET))

        def _parse_gate(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        gate = _parse_gate(d.pop('gate', UNSET))

        def _parse_route_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        route_id = _parse_route_id(d.pop('route_id', UNSET))

        def _parse_route_short_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        route_short_name = _parse_route_short_name(d.pop('route_short_name', UNSET))

        direction_id = d.pop('direction_id', UNSET)

        def _parse_direction_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        direction_text = _parse_direction_text(d.pop('direction_text', UNSET))

        def _parse_terminal(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        terminal = _parse_terminal(d.pop('terminal', UNSET))

        agency_id = d.pop('agency_id', UNSET)

        def _parse_schedule_relationship(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        schedule_relationship = _parse_schedule_relationship(
            d.pop('schedule_relationship', UNSET)
        )

        departure = cls(
            actual=actual,
            trip_id=trip_id,
            stop_id=stop_id,
            departure_text=departure_text,
            departure_time=departure_time,
            description=description,
            gate=gate,
            route_id=route_id,
            route_short_name=route_short_name,
            direction_id=direction_id,
            direction_text=direction_text,
            terminal=terminal,
            agency_id=agency_id,
            schedule_relationship=schedule_relationship,
        )

        return departure
