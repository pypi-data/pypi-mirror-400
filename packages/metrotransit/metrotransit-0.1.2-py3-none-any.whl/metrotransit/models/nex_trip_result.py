from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.alert_message import AlertMessage
    from ..models.departure import Departure
    from ..models.stop import Stop


T = TypeVar('T', bound='NexTripResult')


@_attrs_define
class NexTripResult:
    """Attributes:
    stops (list[Stop] | None | Unset):
    alerts (list[AlertMessage] | None | Unset):
    departures (list[Departure] | None | Unset):
    """

    stops: list[Stop] | None | Unset = UNSET
    alerts: list[AlertMessage] | None | Unset = UNSET
    departures: list[Departure] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        stops: list[dict[str, Any]] | None | Unset
        if isinstance(self.stops, Unset):
            stops = UNSET
        elif isinstance(self.stops, list):
            stops = []
            for stops_type_0_item_data in self.stops:
                stops_type_0_item = stops_type_0_item_data.to_dict()
                stops.append(stops_type_0_item)

        else:
            stops = self.stops

        alerts: list[dict[str, Any]] | None | Unset
        if isinstance(self.alerts, Unset):
            alerts = UNSET
        elif isinstance(self.alerts, list):
            alerts = []
            for alerts_type_0_item_data in self.alerts:
                alerts_type_0_item = alerts_type_0_item_data.to_dict()
                alerts.append(alerts_type_0_item)

        else:
            alerts = self.alerts

        departures: list[dict[str, Any]] | None | Unset
        if isinstance(self.departures, Unset):
            departures = UNSET
        elif isinstance(self.departures, list):
            departures = []
            for departures_type_0_item_data in self.departures:
                departures_type_0_item = departures_type_0_item_data.to_dict()
                departures.append(departures_type_0_item)

        else:
            departures = self.departures

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if stops is not UNSET:
            field_dict['stops'] = stops
        if alerts is not UNSET:
            field_dict['alerts'] = alerts
        if departures is not UNSET:
            field_dict['departures'] = departures

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.alert_message import AlertMessage
        from ..models.departure import Departure
        from ..models.stop import Stop

        d = dict(src_dict)

        def _parse_stops(data: object) -> list[Stop] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError
                stops_type_0 = []
                _stops_type_0 = data
                for stops_type_0_item_data in _stops_type_0:
                    stops_type_0_item = Stop.from_dict(stops_type_0_item_data)

                    stops_type_0.append(stops_type_0_item)

                return stops_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast('list[Stop] | None | Unset', data)

        stops = _parse_stops(d.pop('stops', UNSET))

        def _parse_alerts(data: object) -> list[AlertMessage] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError
                alerts_type_0 = []
                _alerts_type_0 = data
                for alerts_type_0_item_data in _alerts_type_0:
                    alerts_type_0_item = AlertMessage.from_dict(alerts_type_0_item_data)

                    alerts_type_0.append(alerts_type_0_item)

                return alerts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast('list[AlertMessage] | None | Unset', data)

        alerts = _parse_alerts(d.pop('alerts', UNSET))

        def _parse_departures(data: object) -> list[Departure] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError
                departures_type_0 = []
                _departures_type_0 = data
                for departures_type_0_item_data in _departures_type_0:
                    departures_type_0_item = Departure.from_dict(
                        departures_type_0_item_data
                    )

                    departures_type_0.append(departures_type_0_item)

                return departures_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast('list[Departure] | None | Unset', data)

        departures = _parse_departures(d.pop('departures', UNSET))

        nex_trip_result = cls(
            stops=stops,
            alerts=alerts,
            departures=departures,
        )

        return nex_trip_result
