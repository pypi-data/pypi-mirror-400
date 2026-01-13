
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_audit_resources_type_id_response_200_data_item import (
        GetApiV1AdminAuditResourcesTypeIdResponse200DataItem,
    )


T = TypeVar("T", bound="GetApiV1AdminAuditResourcesTypeIdResponse200")


@_attrs_define
class GetApiV1AdminAuditResourcesTypeIdResponse200:
    """
    Attributes:
        data (List['GetApiV1AdminAuditResourcesTypeIdResponse200DataItem']):
        total (float):
        limit (float):
        offset (float):
    """

    data: list["GetApiV1AdminAuditResourcesTypeIdResponse200DataItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_audit_resources_type_id_response_200_data_item import (
            GetApiV1AdminAuditResourcesTypeIdResponse200DataItem,
        )

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiV1AdminAuditResourcesTypeIdResponse200DataItem.from_dict(data_item_data)

            data.append(data_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_admin_audit_resources_type_id_response_200 = cls(
            data=data,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_admin_audit_resources_type_id_response_200
