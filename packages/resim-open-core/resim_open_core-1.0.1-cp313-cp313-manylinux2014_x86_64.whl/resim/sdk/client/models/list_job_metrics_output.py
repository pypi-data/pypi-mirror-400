from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.job_metric import JobMetric





T = TypeVar("T", bound="ListJobMetricsOutput")



@_attrs_define
class ListJobMetricsOutput:
    """ 
        Attributes:
            metrics (list[JobMetric] | Unset):
            next_page_token (str | Unset):
     """

    metrics: list[JobMetric] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.job_metric import JobMetric
        metrics: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = []
            for metrics_item_data in self.metrics:
                metrics_item = metrics_item_data.to_dict()
                metrics.append(metrics_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_metric import JobMetric
        d = dict(src_dict)
        metrics = []
        _metrics = d.pop("metrics", UNSET)
        for metrics_item_data in (_metrics or []):
            metrics_item = JobMetric.from_dict(metrics_item_data)



            metrics.append(metrics_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_job_metrics_output = cls(
            metrics=metrics,
            next_page_token=next_page_token,
        )


        list_job_metrics_output.additional_properties = d
        return list_job_metrics_output

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
