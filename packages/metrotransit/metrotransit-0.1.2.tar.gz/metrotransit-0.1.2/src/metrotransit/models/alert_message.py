from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar('T', bound='AlertMessage')


@_attrs_define
class AlertMessage:
    """Attributes:
    stop_closed (bool | Unset):
    alert_text (None | str | Unset):
    """

    stop_closed: bool | Unset = UNSET
    alert_text: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        stop_closed = self.stop_closed

        alert_text: None | str | Unset
        if isinstance(self.alert_text, Unset):
            alert_text = UNSET
        else:
            alert_text = self.alert_text

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if stop_closed is not UNSET:
            field_dict['stop_closed'] = stop_closed
        if alert_text is not UNSET:
            field_dict['alert_text'] = alert_text

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        stop_closed = d.pop('stop_closed', UNSET)

        def _parse_alert_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast('None | str | Unset', data)

        alert_text = _parse_alert_text(d.pop('alert_text', UNSET))

        alert_message = cls(
            stop_closed=stop_closed,
            alert_text=alert_text,
        )

        return alert_message
