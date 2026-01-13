
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1PositionsPositionIdResponse200HistoryItem")


@_attrs_define
class GetApiV1PositionsPositionIdResponse200HistoryItem:
    """
    Attributes:
        quantity_before (float):
        quantity_after (float):
        quantity_change (float):
        trade_id (Union[None, str]):
        created_at (str):
    """

    quantity_before: float
    quantity_after: float
    quantity_change: float
    trade_id: None | str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        quantity_before = self.quantity_before

        quantity_after = self.quantity_after

        quantity_change = self.quantity_change

        trade_id: None | str
        trade_id = self.trade_id

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "quantityBefore": quantity_before,
                "quantityAfter": quantity_after,
                "quantityChange": quantity_change,
                "tradeId": trade_id,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        quantity_before = d.pop("quantityBefore")

        quantity_after = d.pop("quantityAfter")

        quantity_change = d.pop("quantityChange")

        def _parse_trade_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trade_id = _parse_trade_id(d.pop("tradeId"))

        created_at = d.pop("createdAt")

        get_api_v1_positions_position_id_response_200_history_item = cls(
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            quantity_change=quantity_change,
            trade_id=trade_id,
            created_at=created_at,
        )

        return get_api_v1_positions_position_id_response_200_history_item
