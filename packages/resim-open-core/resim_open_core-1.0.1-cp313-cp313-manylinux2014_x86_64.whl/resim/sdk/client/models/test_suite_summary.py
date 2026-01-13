from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.test_suite_summary_summary import TestSuiteSummarySummary
  from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0
  from ..models.key_metric_type_0 import KeyMetricType0
  from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults





T = TypeVar("T", bound="TestSuiteSummary")



@_attrs_define
class TestSuiteSummary:
    """ 
        Attributes:
            name (str):
            test_suite_id (str):
            test_suite_revision (int):
            test_suite_description (str):
            project_id (str):
            system_id (str):
            branch_id (str):
            report_id (str):
            key_metric (KeyMetricType0 | None):
            reference_batch_summary (None | ReferenceBatchSummaryType0):
            summary (TestSuiteSummarySummary):
            batches (list[TestSuiteBatchSummaryJobResults]):
            reference_batch (TestSuiteBatchSummaryJobResults | Unset):
     """

    name: str
    test_suite_id: str
    test_suite_revision: int
    test_suite_description: str
    project_id: str
    system_id: str
    branch_id: str
    report_id: str
    key_metric: KeyMetricType0 | None
    reference_batch_summary: None | ReferenceBatchSummaryType0
    summary: TestSuiteSummarySummary
    batches: list[TestSuiteBatchSummaryJobResults]
    reference_batch: TestSuiteBatchSummaryJobResults | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.test_suite_summary_summary import TestSuiteSummarySummary
        from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0
        from ..models.key_metric_type_0 import KeyMetricType0
        from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults
        name = self.name

        test_suite_id = self.test_suite_id

        test_suite_revision = self.test_suite_revision

        test_suite_description = self.test_suite_description

        project_id = self.project_id

        system_id = self.system_id

        branch_id = self.branch_id

        report_id = self.report_id

        key_metric: dict[str, Any] | None
        if isinstance(self.key_metric, KeyMetricType0):
            key_metric = self.key_metric.to_dict()
        else:
            key_metric = self.key_metric

        reference_batch_summary: dict[str, Any] | None
        if isinstance(self.reference_batch_summary, ReferenceBatchSummaryType0):
            reference_batch_summary = self.reference_batch_summary.to_dict()
        else:
            reference_batch_summary = self.reference_batch_summary

        summary = self.summary.to_dict()

        batches = []
        for batches_item_data in self.batches:
            batches_item = batches_item_data.to_dict()
            batches.append(batches_item)



        reference_batch: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reference_batch, Unset):
            reference_batch = self.reference_batch.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "testSuiteID": test_suite_id,
            "testSuiteRevision": test_suite_revision,
            "testSuiteDescription": test_suite_description,
            "projectID": project_id,
            "systemID": system_id,
            "branchID": branch_id,
            "reportID": report_id,
            "keyMetric": key_metric,
            "referenceBatchSummary": reference_batch_summary,
            "summary": summary,
            "batches": batches,
        })
        if reference_batch is not UNSET:
            field_dict["referenceBatch"] = reference_batch

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_suite_summary_summary import TestSuiteSummarySummary
        from ..models.reference_batch_summary_type_0 import ReferenceBatchSummaryType0
        from ..models.key_metric_type_0 import KeyMetricType0
        from ..models.test_suite_batch_summary_job_results import TestSuiteBatchSummaryJobResults
        d = dict(src_dict)
        name = d.pop("name")

        test_suite_id = d.pop("testSuiteID")

        test_suite_revision = d.pop("testSuiteRevision")

        test_suite_description = d.pop("testSuiteDescription")

        project_id = d.pop("projectID")

        system_id = d.pop("systemID")

        branch_id = d.pop("branchID")

        report_id = d.pop("reportID")

        def _parse_key_metric(data: object) -> KeyMetricType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemaskey_metric_type_0 = KeyMetricType0.from_dict(data)



                return componentsschemaskey_metric_type_0
            except: # noqa: E722
                pass
            return cast(KeyMetricType0 | None, data)

        key_metric = _parse_key_metric(d.pop("keyMetric"))


        def _parse_reference_batch_summary(data: object) -> None | ReferenceBatchSummaryType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasreference_batch_summary_type_0 = ReferenceBatchSummaryType0.from_dict(data)



                return componentsschemasreference_batch_summary_type_0
            except: # noqa: E722
                pass
            return cast(None | ReferenceBatchSummaryType0, data)

        reference_batch_summary = _parse_reference_batch_summary(d.pop("referenceBatchSummary"))


        summary = TestSuiteSummarySummary.from_dict(d.pop("summary"))




        batches = []
        _batches = d.pop("batches")
        for batches_item_data in (_batches):
            batches_item = TestSuiteBatchSummaryJobResults.from_dict(batches_item_data)



            batches.append(batches_item)


        _reference_batch = d.pop("referenceBatch", UNSET)
        reference_batch: TestSuiteBatchSummaryJobResults | Unset
        if isinstance(_reference_batch,  Unset):
            reference_batch = UNSET
        else:
            reference_batch = TestSuiteBatchSummaryJobResults.from_dict(_reference_batch)




        test_suite_summary = cls(
            name=name,
            test_suite_id=test_suite_id,
            test_suite_revision=test_suite_revision,
            test_suite_description=test_suite_description,
            project_id=project_id,
            system_id=system_id,
            branch_id=branch_id,
            report_id=report_id,
            key_metric=key_metric,
            reference_batch_summary=reference_batch_summary,
            summary=summary,
            batches=batches,
            reference_batch=reference_batch,
        )


        test_suite_summary.additional_properties = d
        return test_suite_summary

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
