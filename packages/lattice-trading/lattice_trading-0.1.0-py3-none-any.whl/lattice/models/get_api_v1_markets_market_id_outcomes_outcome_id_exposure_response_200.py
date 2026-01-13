
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsMarketIdOutcomesOutcomeIdExposureResponse200")


@_attrs_define
class GetApiV1MarketsMarketIdOutcomesOutcomeIdExposureResponse200:
    """
    Attributes:
        outcome_id (str):
        total_long_quantity (float):
        total_short_quantity (float):
        net_exposure (float):
        position_count (float):
    """

    outcome_id: str
    total_long_quantity: float
    total_short_quantity: float
    net_exposure: float
    position_count: float

    def to_dict(self) -> dict[str, Any]:
        outcome_id = self.outcome_id

        total_long_quantity = self.total_long_quantity

        total_short_quantity = self.total_short_quantity

        net_exposure = self.net_exposure

        position_count = self.position_count

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "outcomeId": outcome_id,
                "totalLongQuantity": total_long_quantity,
                "totalShortQuantity": total_short_quantity,
                "netExposure": net_exposure,
                "positionCount": position_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        outcome_id = d.pop("outcomeId")

        total_long_quantity = d.pop("totalLongQuantity")

        total_short_quantity = d.pop("totalShortQuantity")

        net_exposure = d.pop("netExposure")

        position_count = d.pop("positionCount")

        get_api_v1_markets_market_id_outcomes_outcome_id_exposure_response_200 = cls(
            outcome_id=outcome_id,
            total_long_quantity=total_long_quantity,
            total_short_quantity=total_short_quantity,
            net_exposure=net_exposure,
            position_count=position_count,
        )

        return get_api_v1_markets_market_id_outcomes_outcome_id_exposure_response_200
