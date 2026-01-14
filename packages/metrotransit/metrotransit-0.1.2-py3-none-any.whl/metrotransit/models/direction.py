from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Direction')


@_attrs_define
class Direction:
    """Attributes:
    direction_id (int | Unset):
    direction_name (None | str | Unset):
    """

    direction_id: int | Unset = UNSET
    direction_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        direction_id = self.direction_id

        direction_name: None | str | Unset
        if isinstance(self.direction_name, Unset):
            direction_name = UNSET
        else:
            direction_name = self.direction_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if direction_id is not UNSET:
            field_dict['direction_id'] = direction_id
        if direction_name is not UNSET:
            field_dict['direction_name'] = direction_name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        direction_id = d.pop('direction_id', UNSET)

        def _parse_direction_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        direction_name = _parse_direction_name(d.pop('direction_name', UNSET))

        direction = cls(
            direction_id=direction_id,
            direction_name=direction_name,
        )

        return direction
