from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.experience_filter_input import ExperienceFilterInput





T = TypeVar("T", bound="AddSuitesToExperiencesInput")



@_attrs_define
class AddSuitesToExperiencesInput:
    """ 
        Attributes:
            test_suite_i_ds (list[str]):
            experiences (list[str] | Unset):
            all_experiences (bool | Unset):
            filters (ExperienceFilterInput | Unset):
     """

    test_suite_i_ds: list[str]
    experiences: list[str] | Unset = UNSET
    all_experiences: bool | Unset = UNSET
    filters: ExperienceFilterInput | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        test_suite_i_ds = self.test_suite_i_ds



        experiences: list[str] | Unset = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = self.experiences



        all_experiences = self.all_experiences

        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "testSuiteIDs": test_suite_i_ds,
        })
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if all_experiences is not UNSET:
            field_dict["allExperiences"] = all_experiences
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        d = dict(src_dict)
        test_suite_i_ds = cast(list[str], d.pop("testSuiteIDs"))


        experiences = cast(list[str], d.pop("experiences", UNSET))


        all_experiences = d.pop("allExperiences", UNSET)

        _filters = d.pop("filters", UNSET)
        filters: ExperienceFilterInput | Unset
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        add_suites_to_experiences_input = cls(
            test_suite_i_ds=test_suite_i_ds,
            experiences=experiences,
            all_experiences=all_experiences,
            filters=filters,
        )


        add_suites_to_experiences_input.additional_properties = d
        return add_suites_to_experiences_input

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
