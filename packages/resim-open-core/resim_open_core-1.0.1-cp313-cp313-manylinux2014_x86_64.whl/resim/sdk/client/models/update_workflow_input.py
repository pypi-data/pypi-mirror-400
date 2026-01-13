from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="UpdateWorkflowInput")



@_attrs_define
class UpdateWorkflowInput:
    """ 
        Attributes:
            name (str | Unset):
            description (str | Unset):
            ci_workflow_link (None | str | Unset):
     """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    ci_workflow_link: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        ci_workflow_link: None | str | Unset
        if isinstance(self.ci_workflow_link, Unset):
            ci_workflow_link = UNSET
        else:
            ci_workflow_link = self.ci_workflow_link


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if ci_workflow_link is not UNSET:
            field_dict["ciWorkflowLink"] = ci_workflow_link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        def _parse_ci_workflow_link(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ci_workflow_link = _parse_ci_workflow_link(d.pop("ciWorkflowLink", UNSET))


        update_workflow_input = cls(
            name=name,
            description=description,
            ci_workflow_link=ci_workflow_link,
        )


        update_workflow_input.additional_properties = d
        return update_workflow_input

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
