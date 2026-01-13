from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Project")



@_attrs_define
class Project:
    """ 
        Attributes:
            project_id (str):
            name (str):
            description (str):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
            archived (bool):
     """

    project_id: str
    name: str
    description: str
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    archived: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        name = self.name

        description = self.description

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id

        archived = self.archived


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "projectID": project_id,
            "name": name,
            "description": description,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
            "archived": archived,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = d.pop("projectID")

        name = d.pop("name")

        description = d.pop("description")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        archived = d.pop("archived")

        project = cls(
            project_id=project_id,
            name=name,
            description=description,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
            archived=archived,
        )


        project.additional_properties = d
        return project

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
