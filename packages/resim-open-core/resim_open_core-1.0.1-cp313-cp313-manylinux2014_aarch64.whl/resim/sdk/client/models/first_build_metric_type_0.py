from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="FirstBuildMetricType0")



@_attrs_define
class FirstBuildMetricType0:
    """ The first batch metric in the sequence, and some info about how it has changed

        Attributes:
            time (datetime.datetime):
            value (float):  Example: -120.234.
            delta (float):
     """

    time: datetime.datetime
    value: float
    delta: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        time = self.time.isoformat()

        value = self.value

        delta = self.delta


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "time": time,
            "value": value,
            "delta": delta,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time = isoparse(d.pop("time"))




        value = d.pop("value")

        delta = d.pop("delta")

        first_build_metric_type_0 = cls(
            time=time,
            value=value,
            delta=delta,
        )


        first_build_metric_type_0.additional_properties = d
        return first_build_metric_type_0

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
