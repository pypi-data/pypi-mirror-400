from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.environment_variable import EnvironmentVariable





T = TypeVar("T", bound="Experience")



@_attrs_define
class Experience:
    """ 
        Attributes:
            experience_id (str):
            project_id (str):
            name (str):
            description (str):
            location (str): [DEPRECATED] This field was previously used to report an experience's location. Experiences can
                now be defined with multiple locations, this field will display the first location; this field will be removed
                in a future version.
            locations (list[str]):
            container_timeout_seconds (int):
            profile (str):
            environment_variables (list[EnvironmentVariable]):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
            archived (bool):
            cache_exempt (bool):
     """

    experience_id: str
    project_id: str
    name: str
    description: str
    location: str
    locations: list[str]
    container_timeout_seconds: int
    profile: str
    environment_variables: list[EnvironmentVariable]
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    archived: bool
    cache_exempt: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        experience_id = self.experience_id

        project_id = self.project_id

        name = self.name

        description = self.description

        location = self.location

        locations = self.locations



        container_timeout_seconds = self.container_timeout_seconds

        profile = self.profile

        environment_variables = []
        for environment_variables_item_data in self.environment_variables:
            environment_variables_item = environment_variables_item_data.to_dict()
            environment_variables.append(environment_variables_item)



        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id

        archived = self.archived

        cache_exempt = self.cache_exempt


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "experienceID": experience_id,
            "projectID": project_id,
            "name": name,
            "description": description,
            "location": location,
            "locations": locations,
            "containerTimeoutSeconds": container_timeout_seconds,
            "profile": profile,
            "environmentVariables": environment_variables,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
            "archived": archived,
            "cacheExempt": cache_exempt,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        d = dict(src_dict)
        experience_id = d.pop("experienceID")

        project_id = d.pop("projectID")

        name = d.pop("name")

        description = d.pop("description")

        location = d.pop("location")

        locations = cast(list[str], d.pop("locations"))


        container_timeout_seconds = d.pop("containerTimeoutSeconds")

        profile = d.pop("profile")

        environment_variables = []
        _environment_variables = d.pop("environmentVariables")
        for environment_variables_item_data in (_environment_variables):
            environment_variables_item = EnvironmentVariable.from_dict(environment_variables_item_data)



            environment_variables.append(environment_variables_item)


        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        archived = d.pop("archived")

        cache_exempt = d.pop("cacheExempt")

        experience = cls(
            experience_id=experience_id,
            project_id=project_id,
            name=name,
            description=description,
            location=location,
            locations=locations,
            container_timeout_seconds=container_timeout_seconds,
            profile=profile,
            environment_variables=environment_variables,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
            archived=archived,
            cache_exempt=cache_exempt,
        )


        experience.additional_properties = d
        return experience

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
