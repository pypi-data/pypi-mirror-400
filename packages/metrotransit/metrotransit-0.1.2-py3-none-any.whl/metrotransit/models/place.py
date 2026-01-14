from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Place')


@_attrs_define
class Place:
    """Attributes:
    place_code (None | str | Unset):
    description (None | str | Unset):
    """

    place_code: None | str | Unset = UNSET
    description: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        place_code: None | str | Unset
        if isinstance(self.place_code, Unset):
            place_code = UNSET
        else:
            place_code = self.place_code

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if place_code is not UNSET:
            field_dict['place_code'] = place_code
        if description is not UNSET:
            field_dict['description'] = description

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_place_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        place_code = _parse_place_code(d.pop('place_code', UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        description = _parse_description(d.pop('description', UNSET))

        place = cls(
            place_code=place_code,
            description=description,
        )

        return place
