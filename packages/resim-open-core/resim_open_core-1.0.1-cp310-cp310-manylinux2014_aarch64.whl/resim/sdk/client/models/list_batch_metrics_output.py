from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.batch_metric import BatchMetric





T = TypeVar("T", bound="ListBatchMetricsOutput")



@_attrs_define
class ListBatchMetricsOutput:
    """ 
        Attributes:
            batch_metrics (list[BatchMetric] | Unset):
            next_page_token (str | Unset):
     """

    batch_metrics: list[BatchMetric] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_metric import BatchMetric
        batch_metrics: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.batch_metrics, Unset):
            batch_metrics = []
            for batch_metrics_item_data in self.batch_metrics:
                batch_metrics_item = batch_metrics_item_data.to_dict()
                batch_metrics.append(batch_metrics_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metrics is not UNSET:
            field_dict["batchMetrics"] = batch_metrics
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_metric import BatchMetric
        d = dict(src_dict)
        batch_metrics = []
        _batch_metrics = d.pop("batchMetrics", UNSET)
        for batch_metrics_item_data in (_batch_metrics or []):
            batch_metrics_item = BatchMetric.from_dict(batch_metrics_item_data)



            batch_metrics.append(batch_metrics_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_batch_metrics_output = cls(
            batch_metrics=batch_metrics,
            next_page_token=next_page_token,
        )


        list_batch_metrics_output.additional_properties = d
        return list_batch_metrics_output

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
