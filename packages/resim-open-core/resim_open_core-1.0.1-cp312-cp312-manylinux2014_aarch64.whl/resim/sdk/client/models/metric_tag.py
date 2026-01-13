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






T = TypeVar("T", bound="MetricTag")



@_attrs_define
class MetricTag:
    """ 
        Attributes:
            tag_id (str):
            name (str):
            value (str):
            creation_timestamp (datetime.datetime):
            metric_id (str | Unset):
     """

    tag_id: str
    name: str
    value: str
    creation_timestamp: datetime.datetime
    metric_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        tag_id = self.tag_id

        name = self.name

        value = self.value

        creation_timestamp = self.creation_timestamp.isoformat()

        metric_id = self.metric_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "tagID": tag_id,
            "name": name,
            "value": value,
            "creationTimestamp": creation_timestamp,
        })
        if metric_id is not UNSET:
            field_dict["metricID"] = metric_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tag_id = d.pop("tagID")

        name = d.pop("name")

        value = d.pop("value")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        metric_id = d.pop("metricID", UNSET)

        metric_tag = cls(
            tag_id=tag_id,
            name=name,
            value=value,
            creation_timestamp=creation_timestamp,
            metric_id=metric_id,
        )


        metric_tag.additional_properties = d
        return metric_tag

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
