from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="ViewObject")



@_attrs_define
class ViewObject:
    """ 
        Attributes:
            view_session_id (str | Unset):
            friendly_name (str | Unset):
            view_timestamp (datetime.datetime | Unset):
            object_count (int | Unset):
            mcap_url (str | Unset):
            view_url (str | Unset):
            user_id (str | Unset):
            org_id (str | Unset):
     """

    view_session_id: str | Unset = UNSET
    friendly_name: str | Unset = UNSET
    view_timestamp: datetime.datetime | Unset = UNSET
    object_count: int | Unset = UNSET
    mcap_url: str | Unset = UNSET
    view_url: str | Unset = UNSET
    user_id: str | Unset = UNSET
    org_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        view_session_id = self.view_session_id

        friendly_name = self.friendly_name

        view_timestamp: str | Unset = UNSET
        if not isinstance(self.view_timestamp, Unset):
            view_timestamp = self.view_timestamp.isoformat()

        object_count = self.object_count

        mcap_url = self.mcap_url

        view_url = self.view_url

        user_id = self.user_id

        org_id = self.org_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if view_session_id is not UNSET:
            field_dict["viewSessionID"] = view_session_id
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if view_timestamp is not UNSET:
            field_dict["viewTimestamp"] = view_timestamp
        if object_count is not UNSET:
            field_dict["objectCount"] = object_count
        if mcap_url is not UNSET:
            field_dict["mcapURL"] = mcap_url
        if view_url is not UNSET:
            field_dict["viewURL"] = view_url
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if org_id is not UNSET:
            field_dict["orgID"] = org_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        view_session_id = d.pop("viewSessionID", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        _view_timestamp = d.pop("viewTimestamp", UNSET)
        view_timestamp: datetime.datetime | Unset
        if isinstance(_view_timestamp,  Unset):
            view_timestamp = UNSET
        else:
            view_timestamp = isoparse(_view_timestamp)




        object_count = d.pop("objectCount", UNSET)

        mcap_url = d.pop("mcapURL", UNSET)

        view_url = d.pop("viewURL", UNSET)

        user_id = d.pop("userID", UNSET)

        org_id = d.pop("orgID", UNSET)

        view_object = cls(
            view_session_id=view_session_id,
            friendly_name=friendly_name,
            view_timestamp=view_timestamp,
            object_count=object_count,
            mcap_url=mcap_url,
            view_url=view_url,
            user_id=user_id,
            org_id=org_id,
        )


        view_object.additional_properties = d
        return view_object

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
