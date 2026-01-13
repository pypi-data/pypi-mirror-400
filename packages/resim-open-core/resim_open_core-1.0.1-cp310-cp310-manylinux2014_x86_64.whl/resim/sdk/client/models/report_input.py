from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.triggered_via import TriggeredVia
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="ReportInput")



@_attrs_define
class ReportInput:
    """ 
        Attributes:
            test_suite_id (str):
            branch_id (str):
            metrics_build_id (str):
            start_timestamp (datetime.datetime):
            test_suite_revision (int | Unset):
            respect_revision_boundary (bool | Unset):
            metrics_set_name (None | str | Unset):
            end_timestamp (datetime.datetime | Unset):
            name (str | Unset):
            associated_account (str | Unset):
            triggered_via (TriggeredVia | Unset):
            pool_labels (list[str] | Unset):
     """

    test_suite_id: str
    branch_id: str
    metrics_build_id: str
    start_timestamp: datetime.datetime
    test_suite_revision: int | Unset = UNSET
    respect_revision_boundary: bool | Unset = UNSET
    metrics_set_name: None | str | Unset = UNSET
    end_timestamp: datetime.datetime | Unset = UNSET
    name: str | Unset = UNSET
    associated_account: str | Unset = UNSET
    triggered_via: TriggeredVia | Unset = UNSET
    pool_labels: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        test_suite_id = self.test_suite_id

        branch_id = self.branch_id

        metrics_build_id = self.metrics_build_id

        start_timestamp = self.start_timestamp.isoformat()

        test_suite_revision = self.test_suite_revision

        respect_revision_boundary = self.respect_revision_boundary

        metrics_set_name: None | str | Unset
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        end_timestamp: str | Unset = UNSET
        if not isinstance(self.end_timestamp, Unset):
            end_timestamp = self.end_timestamp.isoformat()

        name = self.name

        associated_account = self.associated_account

        triggered_via: str | Unset = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value


        pool_labels: list[str] | Unset = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "testSuiteID": test_suite_id,
            "branchID": branch_id,
            "metricsBuildID": metrics_build_id,
            "startTimestamp": start_timestamp,
        })
        if test_suite_revision is not UNSET:
            field_dict["testSuiteRevision"] = test_suite_revision
        if respect_revision_boundary is not UNSET:
            field_dict["respectRevisionBoundary"] = respect_revision_boundary
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if end_timestamp is not UNSET:
            field_dict["endTimestamp"] = end_timestamp
        if name is not UNSET:
            field_dict["name"] = name
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        test_suite_id = d.pop("testSuiteID")

        branch_id = d.pop("branchID")

        metrics_build_id = d.pop("metricsBuildID")

        start_timestamp = isoparse(d.pop("startTimestamp"))




        test_suite_revision = d.pop("testSuiteRevision", UNSET)

        respect_revision_boundary = d.pop("respectRevisionBoundary", UNSET)

        def _parse_metrics_set_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        _end_timestamp = d.pop("endTimestamp", UNSET)
        end_timestamp: datetime.datetime | Unset
        if isinstance(_end_timestamp,  Unset):
            end_timestamp = UNSET
        else:
            end_timestamp = isoparse(_end_timestamp)




        name = d.pop("name", UNSET)

        associated_account = d.pop("associatedAccount", UNSET)

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: TriggeredVia | Unset
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        pool_labels = cast(list[str], d.pop("poolLabels", UNSET))


        report_input = cls(
            test_suite_id=test_suite_id,
            branch_id=branch_id,
            metrics_build_id=metrics_build_id,
            start_timestamp=start_timestamp,
            test_suite_revision=test_suite_revision,
            respect_revision_boundary=respect_revision_boundary,
            metrics_set_name=metrics_set_name,
            end_timestamp=end_timestamp,
            name=name,
            associated_account=associated_account,
            triggered_via=triggered_via,
            pool_labels=pool_labels,
        )


        report_input.additional_properties = d
        return report_input

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
