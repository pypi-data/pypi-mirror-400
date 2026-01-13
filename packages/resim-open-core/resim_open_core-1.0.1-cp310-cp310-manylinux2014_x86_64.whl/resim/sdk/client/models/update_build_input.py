from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_build_fields import UpdateBuildFields





T = TypeVar("T", bound="UpdateBuildInput")



@_attrs_define
class UpdateBuildInput:
    """ 
        Attributes:
            update_mask (list[str] | Unset):
            build (UpdateBuildFields | Unset):
     """

    update_mask: list[str] | Unset = UNSET
    build: UpdateBuildFields | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_build_fields import UpdateBuildFields
        update_mask: list[str] | Unset = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask



        build: dict[str, Any] | Unset = UNSET
        if not isinstance(self.build, Unset):
            build = self.build.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask
        if build is not UNSET:
            field_dict["build"] = build

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_build_fields import UpdateBuildFields
        d = dict(src_dict)
        update_mask = cast(list[str], d.pop("updateMask", UNSET))


        _build = d.pop("build", UNSET)
        build: UpdateBuildFields | Unset
        if isinstance(_build,  Unset):
            build = UNSET
        else:
            build = UpdateBuildFields.from_dict(_build)




        update_build_input = cls(
            update_mask=update_mask,
            build=build,
        )


        update_build_input.additional_properties = d
        return update_build_input

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
