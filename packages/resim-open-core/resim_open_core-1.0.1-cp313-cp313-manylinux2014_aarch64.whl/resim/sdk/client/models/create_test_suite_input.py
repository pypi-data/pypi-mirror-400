from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.experience_filter_input import ExperienceFilterInput





T = TypeVar("T", bound="CreateTestSuiteInput")



@_attrs_define
class CreateTestSuiteInput:
    """ 
        Attributes:
            name (str):
            description (str):
            system_id (str):
            experiences (list[str]):
            metrics_build_id (str | Unset):
            metrics_set_name (None | str | Unset):
            all_experiences (bool | Unset):
            excluded_experience_i_ds (list[str] | Unset):
            filters (ExperienceFilterInput | Unset):
            show_on_summary (bool | Unset):
            summary_reference_date (datetime.datetime | Unset):
     """

    name: str
    description: str
    system_id: str
    experiences: list[str]
    metrics_build_id: str | Unset = UNSET
    metrics_set_name: None | str | Unset = UNSET
    all_experiences: bool | Unset = UNSET
    excluded_experience_i_ds: list[str] | Unset = UNSET
    filters: ExperienceFilterInput | Unset = UNSET
    show_on_summary: bool | Unset = UNSET
    summary_reference_date: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        name = self.name

        description = self.description

        system_id = self.system_id

        experiences = self.experiences



        metrics_build_id = self.metrics_build_id

        metrics_set_name: None | str | Unset
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        all_experiences = self.all_experiences

        excluded_experience_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.excluded_experience_i_ds, Unset):
            excluded_experience_i_ds = self.excluded_experience_i_ds



        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        show_on_summary = self.show_on_summary

        summary_reference_date: str | Unset = UNSET
        if not isinstance(self.summary_reference_date, Unset):
            summary_reference_date = self.summary_reference_date.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "description": description,
            "systemID": system_id,
            "experiences": experiences,
        })
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if all_experiences is not UNSET:
            field_dict["allExperiences"] = all_experiences
        if excluded_experience_i_ds is not UNSET:
            field_dict["excludedExperienceIDs"] = excluded_experience_i_ds
        if filters is not UNSET:
            field_dict["filters"] = filters
        if show_on_summary is not UNSET:
            field_dict["showOnSummary"] = show_on_summary
        if summary_reference_date is not UNSET:
            field_dict["summaryReferenceDate"] = summary_reference_date

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        system_id = d.pop("systemID")

        experiences = cast(list[str], d.pop("experiences"))


        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        all_experiences = d.pop("allExperiences", UNSET)

        excluded_experience_i_ds = cast(list[str], d.pop("excludedExperienceIDs", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: ExperienceFilterInput | Unset
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        show_on_summary = d.pop("showOnSummary", UNSET)

        _summary_reference_date = d.pop("summaryReferenceDate", UNSET)
        summary_reference_date: datetime.datetime | Unset
        if isinstance(_summary_reference_date,  Unset):
            summary_reference_date = UNSET
        else:
            summary_reference_date = isoparse(_summary_reference_date)




        create_test_suite_input = cls(
            name=name,
            description=description,
            system_id=system_id,
            experiences=experiences,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            all_experiences=all_experiences,
            excluded_experience_i_ds=excluded_experience_i_ds,
            filters=filters,
            show_on_summary=show_on_summary,
            summary_reference_date=summary_reference_date,
        )


        create_test_suite_input.additional_properties = d
        return create_test_suite_input

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
