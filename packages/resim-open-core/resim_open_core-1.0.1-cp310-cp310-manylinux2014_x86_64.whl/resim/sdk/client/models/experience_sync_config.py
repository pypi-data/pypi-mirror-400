from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.experience_sync_test_suite import ExperienceSyncTestSuite
  from ..models.experience_sync_experience import ExperienceSyncExperience





T = TypeVar("T", bound="ExperienceSyncConfig")



@_attrs_define
class ExperienceSyncConfig:
    """ 
        Attributes:
            experiences (list[ExperienceSyncExperience]):
            managed_test_suites (list[ExperienceSyncTestSuite]):
            managed_experience_tags (list[str]):
     """

    experiences: list[ExperienceSyncExperience]
    managed_test_suites: list[ExperienceSyncTestSuite]
    managed_experience_tags: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_sync_test_suite import ExperienceSyncTestSuite
        from ..models.experience_sync_experience import ExperienceSyncExperience
        experiences = []
        for experiences_item_data in self.experiences:
            experiences_item = experiences_item_data.to_dict()
            experiences.append(experiences_item)



        managed_test_suites = []
        for managed_test_suites_item_data in self.managed_test_suites:
            managed_test_suites_item = managed_test_suites_item_data.to_dict()
            managed_test_suites.append(managed_test_suites_item)



        managed_experience_tags = self.managed_experience_tags




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "experiences": experiences,
            "managedTestSuites": managed_test_suites,
            "managedExperienceTags": managed_experience_tags,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_sync_test_suite import ExperienceSyncTestSuite
        from ..models.experience_sync_experience import ExperienceSyncExperience
        d = dict(src_dict)
        experiences = []
        _experiences = d.pop("experiences")
        for experiences_item_data in (_experiences):
            experiences_item = ExperienceSyncExperience.from_dict(experiences_item_data)



            experiences.append(experiences_item)


        managed_test_suites = []
        _managed_test_suites = d.pop("managedTestSuites")
        for managed_test_suites_item_data in (_managed_test_suites):
            managed_test_suites_item = ExperienceSyncTestSuite.from_dict(managed_test_suites_item_data)



            managed_test_suites.append(managed_test_suites_item)


        managed_experience_tags = cast(list[str], d.pop("managedExperienceTags"))


        experience_sync_config = cls(
            experiences=experiences,
            managed_test_suites=managed_test_suites,
            managed_experience_tags=managed_experience_tags,
        )


        experience_sync_config.additional_properties = d
        return experience_sync_config

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
