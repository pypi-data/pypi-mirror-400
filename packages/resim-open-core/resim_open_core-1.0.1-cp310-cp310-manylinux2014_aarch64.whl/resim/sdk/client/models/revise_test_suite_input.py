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





T = TypeVar("T", bound="ReviseTestSuiteInput")



@_attrs_define
class ReviseTestSuiteInput:
    """ 
        Attributes:
            update_metrics_build (bool):
            name (str | Unset):
            description (str | Unset):
            system_id (str | Unset):
            metrics_build_id (str | Unset):
            metrics_set_name (None | str | Unset):
            all_experiences (bool | Unset):
            experiences (list[str] | Unset):
            excluded_experience_i_ds (list[str] | Unset):
            filters (ExperienceFilterInput | Unset):
            adhoc (bool | Unset):
            show_on_summary (bool | Unset):
     """

    update_metrics_build: bool
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    system_id: str | Unset = UNSET
    metrics_build_id: str | Unset = UNSET
    metrics_set_name: None | str | Unset = UNSET
    all_experiences: bool | Unset = UNSET
    experiences: list[str] | Unset = UNSET
    excluded_experience_i_ds: list[str] | Unset = UNSET
    filters: ExperienceFilterInput | Unset = UNSET
    adhoc: bool | Unset = UNSET
    show_on_summary: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        update_metrics_build = self.update_metrics_build

        name = self.name

        description = self.description

        system_id = self.system_id

        metrics_build_id = self.metrics_build_id

        metrics_set_name: None | str | Unset
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        all_experiences = self.all_experiences

        experiences: list[str] | Unset = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = self.experiences



        excluded_experience_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.excluded_experience_i_ds, Unset):
            excluded_experience_i_ds = self.excluded_experience_i_ds



        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        adhoc = self.adhoc

        show_on_summary = self.show_on_summary


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "updateMetricsBuild": update_metrics_build,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if system_id is not UNSET:
            field_dict["systemID"] = system_id
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if all_experiences is not UNSET:
            field_dict["allExperiences"] = all_experiences
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if excluded_experience_i_ds is not UNSET:
            field_dict["excludedExperienceIDs"] = excluded_experience_i_ds
        if filters is not UNSET:
            field_dict["filters"] = filters
        if adhoc is not UNSET:
            field_dict["adhoc"] = adhoc
        if show_on_summary is not UNSET:
            field_dict["show_on_summary"] = show_on_summary

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        d = dict(src_dict)
        update_metrics_build = d.pop("updateMetricsBuild")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        system_id = d.pop("systemID", UNSET)

        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        all_experiences = d.pop("allExperiences", UNSET)

        experiences = cast(list[str], d.pop("experiences", UNSET))


        excluded_experience_i_ds = cast(list[str], d.pop("excludedExperienceIDs", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: ExperienceFilterInput | Unset
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        adhoc = d.pop("adhoc", UNSET)

        show_on_summary = d.pop("show_on_summary", UNSET)

        revise_test_suite_input = cls(
            update_metrics_build=update_metrics_build,
            name=name,
            description=description,
            system_id=system_id,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            all_experiences=all_experiences,
            experiences=experiences,
            excluded_experience_i_ds=excluded_experience_i_ds,
            filters=filters,
            adhoc=adhoc,
            show_on_summary=show_on_summary,
        )


        revise_test_suite_input.additional_properties = d
        return revise_test_suite_input

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
