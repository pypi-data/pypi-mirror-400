from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.project import Project





T = TypeVar("T", bound="ListProjectsOutput")



@_attrs_define
class ListProjectsOutput:
    """ 
        Attributes:
            projects (list[Project] | Unset):
            next_page_token (str | Unset):
     """

    projects: list[Project] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.project import Project
        projects: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.projects, Unset):
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()
                projects.append(projects_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if projects is not UNSET:
            field_dict["projects"] = projects
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project import Project
        d = dict(src_dict)
        projects = []
        _projects = d.pop("projects", UNSET)
        for projects_item_data in (_projects or []):
            projects_item = Project.from_dict(projects_item_data)



            projects.append(projects_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_projects_output = cls(
            projects=projects,
            next_page_token=next_page_token,
        )


        list_projects_output.additional_properties = d
        return list_projects_output

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
