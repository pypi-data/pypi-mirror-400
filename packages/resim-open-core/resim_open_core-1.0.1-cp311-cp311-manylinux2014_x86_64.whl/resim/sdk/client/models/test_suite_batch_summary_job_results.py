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
  from ..models.custom_metric import CustomMetric





T = TypeVar("T", bound="TestSuiteBatchSummaryJobResults")



@_attrs_define
class TestSuiteBatchSummaryJobResults:
    """ 
        Attributes:
            batch_id (str):
            batch_creation_timestamp (datetime.datetime):
            build_id (str):
            build_creation_timestamp (datetime.datetime):
            metrics (list[CustomMetric]):
            total (int):
            queued (int):
            running (int):
            error (int):
            cancelled (int):
            blocker (int):
            warning (int):
            passed (int):
     """

    batch_id: str
    batch_creation_timestamp: datetime.datetime
    build_id: str
    build_creation_timestamp: datetime.datetime
    metrics: list[CustomMetric]
    total: int
    queued: int
    running: int
    error: int
    cancelled: int
    blocker: int
    warning: int
    passed: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_metric import CustomMetric
        batch_id = self.batch_id

        batch_creation_timestamp = self.batch_creation_timestamp.isoformat()

        build_id = self.build_id

        build_creation_timestamp = self.build_creation_timestamp.isoformat()

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)



        total = self.total

        queued = self.queued

        running = self.running

        error = self.error

        cancelled = self.cancelled

        blocker = self.blocker

        warning = self.warning

        passed = self.passed


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "batchID": batch_id,
            "batchCreationTimestamp": batch_creation_timestamp,
            "buildID": build_id,
            "buildCreationTimestamp": build_creation_timestamp,
            "metrics": metrics,
            "total": total,
            "queued": queued,
            "running": running,
            "error": error,
            "cancelled": cancelled,
            "blocker": blocker,
            "warning": warning,
            "passed": passed,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_metric import CustomMetric
        d = dict(src_dict)
        batch_id = d.pop("batchID")

        batch_creation_timestamp = isoparse(d.pop("batchCreationTimestamp"))




        build_id = d.pop("buildID")

        build_creation_timestamp = isoparse(d.pop("buildCreationTimestamp"))




        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in (_metrics):
            metrics_item = CustomMetric.from_dict(metrics_item_data)



            metrics.append(metrics_item)


        total = d.pop("total")

        queued = d.pop("queued")

        running = d.pop("running")

        error = d.pop("error")

        cancelled = d.pop("cancelled")

        blocker = d.pop("blocker")

        warning = d.pop("warning")

        passed = d.pop("passed")

        test_suite_batch_summary_job_results = cls(
            batch_id=batch_id,
            batch_creation_timestamp=batch_creation_timestamp,
            build_id=build_id,
            build_creation_timestamp=build_creation_timestamp,
            metrics=metrics,
            total=total,
            queued=queued,
            running=running,
            error=error,
            cancelled=cancelled,
            blocker=blocker,
            warning=warning,
            passed=passed,
        )


        test_suite_batch_summary_job_results.additional_properties = d
        return test_suite_batch_summary_job_results

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
