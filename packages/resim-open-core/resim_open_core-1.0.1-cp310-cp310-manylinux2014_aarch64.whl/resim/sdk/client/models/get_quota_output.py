from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="GetQuotaOutput")



@_attrs_define
class GetQuotaOutput:
    """ 
        Attributes:
            org_id (str | Unset):
            available_tokens (int | Unset):
            max_tokens (int | Unset):
            seconds_until_refresh (int | Unset):
     """

    org_id: str | Unset = UNSET
    available_tokens: int | Unset = UNSET
    max_tokens: int | Unset = UNSET
    seconds_until_refresh: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        org_id = self.org_id

        available_tokens = self.available_tokens

        max_tokens = self.max_tokens

        seconds_until_refresh = self.seconds_until_refresh


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if available_tokens is not UNSET:
            field_dict["availableTokens"] = available_tokens
        if max_tokens is not UNSET:
            field_dict["maxTokens"] = max_tokens
        if seconds_until_refresh is not UNSET:
            field_dict["secondsUntilRefresh"] = seconds_until_refresh

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        org_id = d.pop("orgID", UNSET)

        available_tokens = d.pop("availableTokens", UNSET)

        max_tokens = d.pop("maxTokens", UNSET)

        seconds_until_refresh = d.pop("secondsUntilRefresh", UNSET)

        get_quota_output = cls(
            org_id=org_id,
            available_tokens=available_tokens,
            max_tokens=max_tokens,
            seconds_until_refresh=seconds_until_refresh,
        )


        get_quota_output.additional_properties = d
        return get_quota_output

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
