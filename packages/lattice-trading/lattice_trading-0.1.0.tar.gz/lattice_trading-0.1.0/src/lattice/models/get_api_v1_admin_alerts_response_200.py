
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_alerts_response_200_alerts_item import GetApiV1AdminAlertsResponse200AlertsItem


T = TypeVar("T", bound="GetApiV1AdminAlertsResponse200")


@_attrs_define
class GetApiV1AdminAlertsResponse200:
    """
    Attributes:
        alerts (List['GetApiV1AdminAlertsResponse200AlertsItem']):
        total (float):
        limit (float):
        offset (float):
    """

    alerts: list["GetApiV1AdminAlertsResponse200AlertsItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        alerts = []
        for alerts_item_data in self.alerts:
            alerts_item = alerts_item_data.to_dict()
            alerts.append(alerts_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "alerts": alerts,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_alerts_response_200_alerts_item import GetApiV1AdminAlertsResponse200AlertsItem

        d = src_dict.copy()
        alerts = []
        _alerts = d.pop("alerts")
        for alerts_item_data in _alerts:
            alerts_item = GetApiV1AdminAlertsResponse200AlertsItem.from_dict(alerts_item_data)

            alerts.append(alerts_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_admin_alerts_response_200 = cls(
            alerts=alerts,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_admin_alerts_response_200
