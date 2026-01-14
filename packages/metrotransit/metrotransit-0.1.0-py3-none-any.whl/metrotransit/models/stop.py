from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Stop')


@_attrs_define
class Stop:
    """Attributes:
    stop_id (int | Unset):
    latitude (float | Unset):
    longitude (float | Unset):
    description (None | str | Unset):
    """

    stop_id: int | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    description: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        stop_id = self.stop_id

        latitude = self.latitude

        longitude = self.longitude

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if stop_id is not UNSET:
            field_dict['stop_id'] = stop_id
        if latitude is not UNSET:
            field_dict['latitude'] = latitude
        if longitude is not UNSET:
            field_dict['longitude'] = longitude
        if description is not UNSET:
            field_dict['description'] = description

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        stop_id = d.pop('stop_id', UNSET)

        latitude = d.pop('latitude', UNSET)

        longitude = d.pop('longitude', UNSET)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        description = _parse_description(d.pop('description', UNSET))

        stop = cls(
            stop_id=stop_id,
            latitude=latitude,
            longitude=longitude,
            description=description,
        )

        return stop
