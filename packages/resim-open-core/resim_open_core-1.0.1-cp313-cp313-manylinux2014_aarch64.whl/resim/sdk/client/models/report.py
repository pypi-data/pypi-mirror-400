from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.metric_status import MetricStatus
from ..models.report_status import ReportStatus
from ..models.triggered_via import TriggeredVia
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.report_status_history_type import ReportStatusHistoryType





T = TypeVar("T", bound="Report")



@_attrs_define
class Report:
    """ 
        Attributes:
            report_id (str):
            project_id (str):
            test_suite_id (str):
            test_suite_revision (int):
            respect_revision_boundary (bool):
            branch_id (str):
            metrics_build_id (str):
            metrics_set_name (None | str):
            start_timestamp (datetime.datetime):
            end_timestamp (datetime.datetime):
            name (str):
            output_location (str):
            status (ReportStatus):
            status_history (list[ReportStatusHistoryType]):
            last_updated_timestamp (datetime.datetime):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
            associated_account (str):
            metrics_status (MetricStatus):
            triggered_via (TriggeredVia | Unset):
     """

    report_id: str
    project_id: str
    test_suite_id: str
    test_suite_revision: int
    respect_revision_boundary: bool
    branch_id: str
    metrics_build_id: str
    metrics_set_name: None | str
    start_timestamp: datetime.datetime
    end_timestamp: datetime.datetime
    name: str
    output_location: str
    status: ReportStatus
    status_history: list[ReportStatusHistoryType]
    last_updated_timestamp: datetime.datetime
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    associated_account: str
    metrics_status: MetricStatus
    triggered_via: TriggeredVia | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.report_status_history_type import ReportStatusHistoryType
        report_id = self.report_id

        project_id = self.project_id

        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        respect_revision_boundary = self.respect_revision_boundary

        branch_id = self.branch_id

        metrics_build_id = self.metrics_build_id

        metrics_set_name: None | str
        metrics_set_name = self.metrics_set_name

        start_timestamp = self.start_timestamp.isoformat()

        end_timestamp = self.end_timestamp.isoformat()

        name = self.name

        output_location = self.output_location

        status = self.status.value

        status_history = []
        for componentsschemasreport_status_history_item_data in self.status_history:
            componentsschemasreport_status_history_item = componentsschemasreport_status_history_item_data.to_dict()
            status_history.append(componentsschemasreport_status_history_item)



        last_updated_timestamp = self.last_updated_timestamp.isoformat()

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id

        associated_account = self.associated_account

        metrics_status = self.metrics_status.value

        triggered_via: str | Unset = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "reportID": report_id,
            "projectID": project_id,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
            "respectRevisionBoundary": respect_revision_boundary,
            "branchID": branch_id,
            "metricsBuildID": metrics_build_id,
            "metricsSetName": metrics_set_name,
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "name": name,
            "outputLocation": output_location,
            "status": status,
            "statusHistory": status_history,
            "lastUpdatedTimestamp": last_updated_timestamp,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
            "associatedAccount": associated_account,
            "metricsStatus": metrics_status,
        })
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_status_history_type import ReportStatusHistoryType
        d = dict(src_dict)
        report_id = d.pop("reportID")

        project_id = d.pop("projectID")

        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        respect_revision_boundary = d.pop("respectRevisionBoundary")

        branch_id = d.pop("branchID")

        metrics_build_id = d.pop("metricsBuildID")

        def _parse_metrics_set_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName"))


        start_timestamp = isoparse(d.pop("startTimestamp"))




        end_timestamp = isoparse(d.pop("endTimestamp"))




        name = d.pop("name")

        output_location = d.pop("outputLocation")

        status = ReportStatus(d.pop("status"))




        status_history = []
        _status_history = d.pop("statusHistory")
        for componentsschemasreport_status_history_item_data in (_status_history):
            componentsschemasreport_status_history_item = ReportStatusHistoryType.from_dict(componentsschemasreport_status_history_item_data)



            status_history.append(componentsschemasreport_status_history_item)


        last_updated_timestamp = isoparse(d.pop("lastUpdatedTimestamp"))




        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        associated_account = d.pop("associatedAccount")

        metrics_status = MetricStatus(d.pop("metricsStatus"))




        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: TriggeredVia | Unset
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        report = cls(
            report_id=report_id,
            project_id=project_id,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            respect_revision_boundary=respect_revision_boundary,
            branch_id=branch_id,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            name=name,
            output_location=output_location,
            status=status,
            status_history=status_history,
            last_updated_timestamp=last_updated_timestamp,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
            associated_account=associated_account,
            metrics_status=metrics_status,
            triggered_via=triggered_via,
        )


        report.additional_properties = d
        return report

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
