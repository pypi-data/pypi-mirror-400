
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MetricsOverviewResponse200")


@_attrs_define
class GetApiV1MetricsOverviewResponse200:
    """
    Attributes:
        volume_cents (float):
        open_interest (float):
        active_markets (float):
        active_users (float):
        updated_at (str):
    """

    volume_cents: float
    open_interest: float
    active_markets: float
    active_users: float
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        volume_cents = self.volume_cents

        open_interest = self.open_interest

        active_markets = self.active_markets

        active_users = self.active_users

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "volumeCents": volume_cents,
                "openInterest": open_interest,
                "activeMarkets": active_markets,
                "activeUsers": active_users,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        volume_cents = d.pop("volumeCents")

        open_interest = d.pop("openInterest")

        active_markets = d.pop("activeMarkets")

        active_users = d.pop("activeUsers")

        updated_at = d.pop("updatedAt")

        get_api_v1_metrics_overview_response_200 = cls(
            volume_cents=volume_cents,
            open_interest=open_interest,
            active_markets=active_markets,
            active_users=active_users,
            updated_at=updated_at,
        )

        return get_api_v1_metrics_overview_response_200
