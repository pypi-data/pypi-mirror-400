
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1AdminMarketsMarketIdResolveBody")


@_attrs_define
class PostApiV1AdminMarketsMarketIdResolveBody:
    """
    Attributes:
        outcome_id (str):
        resolution (Union[Unset, str]):
        resolution_source (Union[Unset, str]):
        resolution_notes (Union[Unset, str]):
    """

    outcome_id: str
    resolution: Unset | str = UNSET
    resolution_source: Unset | str = UNSET
    resolution_notes: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        outcome_id = self.outcome_id

        resolution = self.resolution

        resolution_source = self.resolution_source

        resolution_notes = self.resolution_notes

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "outcomeId": outcome_id,
            }
        )
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if resolution_source is not UNSET:
            field_dict["resolutionSource"] = resolution_source
        if resolution_notes is not UNSET:
            field_dict["resolutionNotes"] = resolution_notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        outcome_id = d.pop("outcomeId")

        resolution = d.pop("resolution", UNSET)

        resolution_source = d.pop("resolutionSource", UNSET)

        resolution_notes = d.pop("resolutionNotes", UNSET)

        post_api_v1_admin_markets_market_id_resolve_body = cls(
            outcome_id=outcome_id,
            resolution=resolution,
            resolution_source=resolution_source,
            resolution_notes=resolution_notes,
        )

        return post_api_v1_admin_markets_market_id_resolve_body
