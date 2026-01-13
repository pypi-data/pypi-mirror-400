from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.branch_type import BranchType
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Branch")



@_attrs_define
class Branch:
    """ 
        Attributes:
            branch_id (str):
            name (str):
            project_id (str):
            branch_type (BranchType):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
     """

    branch_id: str
    name: str
    project_id: str
    branch_type: BranchType
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        branch_id = self.branch_id

        name = self.name

        project_id = self.project_id

        branch_type = self.branch_type.value

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "branchID": branch_id,
            "name": name,
            "projectID": project_id,
            "branchType": branch_type,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        branch_id = d.pop("branchID")

        name = d.pop("name")

        project_id = d.pop("projectID")

        branch_type = BranchType(d.pop("branchType"))




        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        branch = cls(
            branch_id=branch_id,
            name=name,
            project_id=project_id,
            branch_type=branch_type,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
        )


        branch.additional_properties = d
        return branch

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
