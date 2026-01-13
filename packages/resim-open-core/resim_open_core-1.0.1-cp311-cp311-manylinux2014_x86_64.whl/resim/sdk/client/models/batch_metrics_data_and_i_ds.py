from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.batch_metrics_data import BatchMetricsData





T = TypeVar("T", bound="BatchMetricsDataAndIDs")



@_attrs_define
class BatchMetricsDataAndIDs:
    """ 
        Attributes:
            batch_metric_id (str | Unset):
            batch_metrics_data (BatchMetricsData | Unset):
     """

    batch_metric_id: str | Unset = UNSET
    batch_metrics_data: BatchMetricsData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_metrics_data import BatchMetricsData
        batch_metric_id = self.batch_metric_id

        batch_metrics_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.batch_metrics_data, Unset):
            batch_metrics_data = self.batch_metrics_data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metric_id is not UNSET:
            field_dict["batchMetricID"] = batch_metric_id
        if batch_metrics_data is not UNSET:
            field_dict["batchMetricsData"] = batch_metrics_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_metrics_data import BatchMetricsData
        d = dict(src_dict)
        batch_metric_id = d.pop("batchMetricID", UNSET)

        _batch_metrics_data = d.pop("batchMetricsData", UNSET)
        batch_metrics_data: BatchMetricsData | Unset
        if isinstance(_batch_metrics_data,  Unset):
            batch_metrics_data = UNSET
        else:
            batch_metrics_data = BatchMetricsData.from_dict(_batch_metrics_data)




        batch_metrics_data_and_i_ds = cls(
            batch_metric_id=batch_metric_id,
            batch_metrics_data=batch_metrics_data,
        )


        batch_metrics_data_and_i_ds.additional_properties = d
        return batch_metrics_data_and_i_ds

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
