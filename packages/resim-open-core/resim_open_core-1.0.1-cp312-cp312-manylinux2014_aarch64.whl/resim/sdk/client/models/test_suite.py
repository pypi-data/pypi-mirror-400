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






T = TypeVar("T", bound="TestSuite")



@_attrs_define
class TestSuite:
    """ 
        Attributes:
            archived (bool):
            test_suite_id (str):
            test_suite_revision (int):
            name (str):
            description (str):
            project_id (str):
            system_id (str):
            experiences (list[str]):
            user_id (str):
            org_id (str):
            creation_timestamp (datetime.datetime):
            show_on_summary (bool):
            metrics_build_id (str | Unset):
            metrics_set_name (None | str | Unset):
            summary_reference_date (datetime.datetime | Unset):
     """

    archived: bool
    test_suite_id: str
    test_suite_revision: int
    name: str
    description: str
    project_id: str
    system_id: str
    experiences: list[str]
    user_id: str
    org_id: str
    creation_timestamp: datetime.datetime
    show_on_summary: bool
    metrics_build_id: str | Unset = UNSET
    metrics_set_name: None | str | Unset = UNSET
    summary_reference_date: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        archived = self.archived

        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        name = self.name

        description = self.description

        project_id = self.project_id

        system_id = self.system_id

        experiences = self.experiences



        user_id = self.user_id

        org_id = self.org_id

        creation_timestamp = self.creation_timestamp.isoformat()

        show_on_summary = self.show_on_summary

        metrics_build_id = self.metrics_build_id

        metrics_set_name: None | str | Unset
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        summary_reference_date: str | Unset = UNSET
        if not isinstance(self.summary_reference_date, Unset):
            summary_reference_date = self.summary_reference_date.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "archived": archived,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
            "name": name,
            "description": description,
            "projectID": project_id,
            "systemID": system_id,
            "experiences": experiences,
            "userID": user_id,
            "orgID": org_id,
            "creationTimestamp": creation_timestamp,
            "showOnSummary": show_on_summary,
        })
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if summary_reference_date is not UNSET:
            field_dict["summaryReferenceDate"] = summary_reference_date

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        archived = d.pop("archived")

        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        name = d.pop("name")

        description = d.pop("description")

        project_id = d.pop("projectID")

        system_id = d.pop("systemID")

        experiences = cast(list[str], d.pop("experiences"))


        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        show_on_summary = d.pop("showOnSummary")

        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        _summary_reference_date = d.pop("summaryReferenceDate", UNSET)
        summary_reference_date: datetime.datetime | Unset
        if isinstance(_summary_reference_date,  Unset):
            summary_reference_date = UNSET
        else:
            summary_reference_date = isoparse(_summary_reference_date)




        test_suite = cls(
            archived=archived,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            name=name,
            description=description,
            project_id=project_id,
            system_id=system_id,
            experiences=experiences,
            user_id=user_id,
            org_id=org_id,
            creation_timestamp=creation_timestamp,
            show_on_summary=show_on_summary,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            summary_reference_date=summary_reference_date,
        )


        test_suite.additional_properties = d
        return test_suite

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
