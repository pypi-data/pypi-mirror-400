from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.object_type import ObjectType
from ..types import UNSET, Unset






T = TypeVar("T", bound="ViewMetadata")



@_attrs_define
class ViewMetadata:
    """ 
        Attributes:
            object_name (str | Unset):
            object_type (ObjectType | Unset):
            file_name (str | Unset):
            line_number (int | Unset):
     """

    object_name: str | Unset = UNSET
    object_type: ObjectType | Unset = UNSET
    file_name: str | Unset = UNSET
    line_number: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        object_name = self.object_name

        object_type: str | Unset = UNSET
        if not isinstance(self.object_type, Unset):
            object_type = self.object_type.value


        file_name = self.file_name

        line_number = self.line_number


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if object_name is not UNSET:
            field_dict["objectName"] = object_name
        if object_type is not UNSET:
            field_dict["objectType"] = object_type
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if line_number is not UNSET:
            field_dict["lineNumber"] = line_number

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        object_name = d.pop("objectName", UNSET)

        _object_type = d.pop("objectType", UNSET)
        object_type: ObjectType | Unset
        if isinstance(_object_type,  Unset):
            object_type = UNSET
        else:
            object_type = ObjectType(_object_type)




        file_name = d.pop("fileName", UNSET)

        line_number = d.pop("lineNumber", UNSET)

        view_metadata = cls(
            object_name=object_name,
            object_type=object_type,
            file_name=file_name,
            line_number=line_number,
        )


        view_metadata.additional_properties = d
        return view_metadata

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
