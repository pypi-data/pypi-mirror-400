from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Route')


@_attrs_define
class Route:
    """Attributes:
    route_id (None | str | Unset):
    agency_id (int | Unset):
    route_label (None | str | Unset):
    """

    route_id: None | str | Unset = UNSET
    agency_id: int | Unset = UNSET
    route_label: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        route_id: None | str | Unset
        if isinstance(self.route_id, Unset):
            route_id = UNSET
        else:
            route_id = self.route_id

        agency_id = self.agency_id

        route_label: None | str | Unset
        if isinstance(self.route_label, Unset):
            route_label = UNSET
        else:
            route_label = self.route_label

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if route_id is not UNSET:
            field_dict['route_id'] = route_id
        if agency_id is not UNSET:
            field_dict['agency_id'] = agency_id
        if route_label is not UNSET:
            field_dict['route_label'] = route_label

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_route_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        route_id = _parse_route_id(d.pop('route_id', UNSET))

        agency_id = d.pop('agency_id', UNSET)

        def _parse_route_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        route_label = _parse_route_label(d.pop('route_label', UNSET))

        route = cls(
            route_id=route_id,
            agency_id=agency_id,
            route_label=route_label,
        )

        return route
