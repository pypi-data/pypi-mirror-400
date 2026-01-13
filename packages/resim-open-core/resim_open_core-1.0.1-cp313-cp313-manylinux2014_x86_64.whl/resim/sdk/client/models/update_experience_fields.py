from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.environment_variable import EnvironmentVariable





T = TypeVar("T", bound="UpdateExperienceFields")



@_attrs_define
class UpdateExperienceFields:
    """ 
        Attributes:
            name (str | Unset):
            description (str | Unset):
            location (str | Unset): [DEPRECATED] This field was previously used to define an experience's location.
                Experiences can now be defined with multiple locations, using the locations field. This field will be removed in
                a future version.
            locations (list[str] | Unset):
            container_timeout_seconds (int | Unset):
            profile (str | Unset):
            environment_variables (list[EnvironmentVariable] | Unset):
            system_i_ds (list[str] | Unset):
            experience_tag_i_ds (list[str] | Unset):
            cache_exempt (bool | Unset): If true, the experience will not be cached.
     """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    location: str | Unset = UNSET
    locations: list[str] | Unset = UNSET
    container_timeout_seconds: int | Unset = UNSET
    profile: str | Unset = UNSET
    environment_variables: list[EnvironmentVariable] | Unset = UNSET
    system_i_ds: list[str] | Unset = UNSET
    experience_tag_i_ds: list[str] | Unset = UNSET
    cache_exempt: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        name = self.name

        description = self.description

        location = self.location

        locations: list[str] | Unset = UNSET
        if not isinstance(self.locations, Unset):
            locations = self.locations



        container_timeout_seconds = self.container_timeout_seconds

        profile = self.profile

        environment_variables: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = []
            for environment_variables_item_data in self.environment_variables:
                environment_variables_item = environment_variables_item_data.to_dict()
                environment_variables.append(environment_variables_item)



        system_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.system_i_ds, Unset):
            system_i_ds = self.system_i_ds



        experience_tag_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.experience_tag_i_ds, Unset):
            experience_tag_i_ds = self.experience_tag_i_ds



        cache_exempt = self.cache_exempt


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if location is not UNSET:
            field_dict["location"] = location
        if locations is not UNSET:
            field_dict["locations"] = locations
        if container_timeout_seconds is not UNSET:
            field_dict["containerTimeoutSeconds"] = container_timeout_seconds
        if profile is not UNSET:
            field_dict["profile"] = profile
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if system_i_ds is not UNSET:
            field_dict["systemIDs"] = system_i_ds
        if experience_tag_i_ds is not UNSET:
            field_dict["experienceTagIDs"] = experience_tag_i_ds
        if cache_exempt is not UNSET:
            field_dict["cacheExempt"] = cache_exempt

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        location = d.pop("location", UNSET)

        locations = cast(list[str], d.pop("locations", UNSET))


        container_timeout_seconds = d.pop("containerTimeoutSeconds", UNSET)

        profile = d.pop("profile", UNSET)

        environment_variables = []
        _environment_variables = d.pop("environmentVariables", UNSET)
        for environment_variables_item_data in (_environment_variables or []):
            environment_variables_item = EnvironmentVariable.from_dict(environment_variables_item_data)



            environment_variables.append(environment_variables_item)


        system_i_ds = cast(list[str], d.pop("systemIDs", UNSET))


        experience_tag_i_ds = cast(list[str], d.pop("experienceTagIDs", UNSET))


        cache_exempt = d.pop("cacheExempt", UNSET)

        update_experience_fields = cls(
            name=name,
            description=description,
            location=location,
            locations=locations,
            container_timeout_seconds=container_timeout_seconds,
            profile=profile,
            environment_variables=environment_variables,
            system_i_ds=system_i_ds,
            experience_tag_i_ds=experience_tag_i_ds,
            cache_exempt=cache_exempt,
        )


        update_experience_fields.additional_properties = d
        return update_experience_fields

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
