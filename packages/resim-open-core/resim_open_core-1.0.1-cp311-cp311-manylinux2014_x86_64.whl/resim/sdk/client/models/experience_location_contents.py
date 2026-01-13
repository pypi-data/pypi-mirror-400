from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="ExperienceLocationContents")



@_attrs_define
class ExperienceLocationContents:
    """ 
        Attributes:
            is_cloud (bool | Unset):
            objects (list[str] | Unset):
            object_count (int | Unset):
     """

    is_cloud: bool | Unset = UNSET
    objects: list[str] | Unset = UNSET
    object_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        is_cloud = self.is_cloud

        objects: list[str] | Unset = UNSET
        if not isinstance(self.objects, Unset):
            objects = self.objects



        object_count = self.object_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if is_cloud is not UNSET:
            field_dict["isCloud"] = is_cloud
        if objects is not UNSET:
            field_dict["objects"] = objects
        if object_count is not UNSET:
            field_dict["objectCount"] = object_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_cloud = d.pop("isCloud", UNSET)

        objects = cast(list[str], d.pop("objects", UNSET))


        object_count = d.pop("objectCount", UNSET)

        experience_location_contents = cls(
            is_cloud=is_cloud,
            objects=objects,
            object_count=object_count,
        )


        experience_location_contents.additional_properties = d
        return experience_location_contents

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
