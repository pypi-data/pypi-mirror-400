from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Build")



@_attrs_define
class Build:
    """ 
        Attributes:
            build_id (str):
            branch_id (str):
            project_id (str):
            system_id (str):
            description (str): The description of the build. May be a SHA or commit message.
            version (str):
            image_uri (str):
            build_specification (str): Build spec in YAML format.
            creation_timestamp (datetime.datetime):
            update_timestamp (datetime.datetime):
            associated_account (str):
            user_id (str):
            org_id (str):
            name (str): The name of the build.
     """

    build_id: str
    branch_id: str
    project_id: str
    system_id: str
    description: str
    version: str
    image_uri: str
    build_specification: str
    creation_timestamp: datetime.datetime
    update_timestamp: datetime.datetime
    associated_account: str
    user_id: str
    org_id: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        build_id = self.build_id

        branch_id = self.branch_id

        project_id = self.project_id

        system_id = self.system_id

        description = self.description

        version = self.version

        image_uri = self.image_uri

        build_specification = self.build_specification

        creation_timestamp = self.creation_timestamp.isoformat()

        update_timestamp = self.update_timestamp.isoformat()

        associated_account = self.associated_account

        user_id = self.user_id

        org_id = self.org_id

        name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "buildID": build_id,
            "branchID": branch_id,
            "projectID": project_id,
            "systemID": system_id,
            "description": description,
            "version": version,
            "imageUri": image_uri,
            "buildSpecification": build_specification,
            "creationTimestamp": creation_timestamp,
            "updateTimestamp": update_timestamp,
            "associatedAccount": associated_account,
            "userID": user_id,
            "orgID": org_id,
            "name": name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        build_id = d.pop("buildID")

        branch_id = d.pop("branchID")

        project_id = d.pop("projectID")

        system_id = d.pop("systemID")

        description = d.pop("description")

        version = d.pop("version")

        image_uri = d.pop("imageUri")

        build_specification = d.pop("buildSpecification")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        update_timestamp = isoparse(d.pop("updateTimestamp"))




        associated_account = d.pop("associatedAccount")

        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        name = d.pop("name")

        build = cls(
            build_id=build_id,
            branch_id=branch_id,
            project_id=project_id,
            system_id=system_id,
            description=description,
            version=version,
            image_uri=image_uri,
            build_specification=build_specification,
            creation_timestamp=creation_timestamp,
            update_timestamp=update_timestamp,
            associated_account=associated_account,
            user_id=user_id,
            org_id=org_id,
            name=name,
        )


        build.additional_properties = d
        return build

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
