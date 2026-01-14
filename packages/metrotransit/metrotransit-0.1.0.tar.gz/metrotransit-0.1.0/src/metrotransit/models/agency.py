from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='Agency')


@_attrs_define
class Agency:
    """Attributes:
    agency_id (int | Unset):
    agency_name (None | str | Unset):
    """

    agency_id: int | Unset = UNSET
    agency_name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        agency_id = self.agency_id

        agency_name: None | str | Unset
        if isinstance(self.agency_name, Unset):
            agency_name = UNSET
        else:
            agency_name = self.agency_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if agency_id is not UNSET:
            field_dict['agency_id'] = agency_id
        if agency_name is not UNSET:
            field_dict['agency_name'] = agency_name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        agency_id = d.pop('agency_id', UNSET)

        def _parse_agency_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        agency_name = _parse_agency_name(d.pop('agency_name', UNSET))

        agency = cls(
            agency_id=agency_id,
            agency_name=agency_name,
        )

        return agency
