
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1WsTokenResponse200")


@_attrs_define
class PostApiV1WsTokenResponse200:
    """
    Attributes:
        token (str):
        expires_in (float):
    """

    token: str
    expires_in: float

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "token": token,
                "expiresIn": expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        token = d.pop("token")

        expires_in = d.pop("expiresIn")

        post_api_v1_ws_token_response_200 = cls(
            token=token,
            expires_in=expires_in,
        )

        return post_api_v1_ws_token_response_200
