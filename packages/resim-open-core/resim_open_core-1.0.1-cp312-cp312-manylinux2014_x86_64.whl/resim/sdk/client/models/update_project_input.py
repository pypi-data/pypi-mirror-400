from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_project_fields import UpdateProjectFields





T = TypeVar("T", bound="UpdateProjectInput")



@_attrs_define
class UpdateProjectInput:
    """ 
        Attributes:
            update_mask (list[str] | Unset):
            project (UpdateProjectFields | Unset):
     """

    update_mask: list[str] | Unset = UNSET
    project: UpdateProjectFields | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_project_fields import UpdateProjectFields
        update_mask: list[str] | Unset = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask



        project: dict[str, Any] | Unset = UNSET
        if not isinstance(self.project, Unset):
            project = self.project.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask
        if project is not UNSET:
            field_dict["project"] = project

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_project_fields import UpdateProjectFields
        d = dict(src_dict)
        update_mask = cast(list[str], d.pop("updateMask", UNSET))


        _project = d.pop("project", UNSET)
        project: UpdateProjectFields | Unset
        if isinstance(_project,  Unset):
            project = UNSET
        else:
            project = UpdateProjectFields.from_dict(_project)




        update_project_input = cls(
            update_mask=update_mask,
            project=project,
        )


        update_project_input.additional_properties = d
        return update_project_input

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
