from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateBuildFields")



@_attrs_define
class UpdateBuildFields:
    """ 
        Attributes:
            branch_id (str | Unset):
            description (str | Unset): The description of the build. May be a SHA or commit message.
            name (str | Unset): The name of the build.
     """

    branch_id: str | Unset = UNSET
    description: str | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        branch_id = self.branch_id

        description = self.description

        name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if branch_id is not UNSET:
            field_dict["branchID"] = branch_id
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        branch_id = d.pop("branchID", UNSET)

        description = d.pop("description", UNSET)

        name = d.pop("name", UNSET)

        update_build_fields = cls(
            branch_id=branch_id,
            description=description,
            name=name,
        )


        update_build_fields.additional_properties = d
        return update_build_fields

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
