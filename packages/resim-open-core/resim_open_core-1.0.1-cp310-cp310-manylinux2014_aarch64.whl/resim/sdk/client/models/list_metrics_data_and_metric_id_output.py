from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.metrics_data_and_metric_id import MetricsDataAndMetricID





T = TypeVar("T", bound="ListMetricsDataAndMetricIDOutput")



@_attrs_define
class ListMetricsDataAndMetricIDOutput:
    """ 
        Attributes:
            metrics_data_and_i_ds (list[MetricsDataAndMetricID] | Unset):
            next_page_token (str | Unset):
     """

    metrics_data_and_i_ds: list[MetricsDataAndMetricID] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.metrics_data_and_metric_id import MetricsDataAndMetricID
        metrics_data_and_i_ds: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.metrics_data_and_i_ds, Unset):
            metrics_data_and_i_ds = []
            for metrics_data_and_i_ds_item_data in self.metrics_data_and_i_ds:
                metrics_data_and_i_ds_item = metrics_data_and_i_ds_item_data.to_dict()
                metrics_data_and_i_ds.append(metrics_data_and_i_ds_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if metrics_data_and_i_ds is not UNSET:
            field_dict["metricsDataAndIDs"] = metrics_data_and_i_ds
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metrics_data_and_metric_id import MetricsDataAndMetricID
        d = dict(src_dict)
        metrics_data_and_i_ds = []
        _metrics_data_and_i_ds = d.pop("metricsDataAndIDs", UNSET)
        for metrics_data_and_i_ds_item_data in (_metrics_data_and_i_ds or []):
            metrics_data_and_i_ds_item = MetricsDataAndMetricID.from_dict(metrics_data_and_i_ds_item_data)



            metrics_data_and_i_ds.append(metrics_data_and_i_ds_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_metrics_data_and_metric_id_output = cls(
            metrics_data_and_i_ds=metrics_data_and_i_ds,
            next_page_token=next_page_token,
        )


        list_metrics_data_and_metric_id_output.additional_properties = d
        return list_metrics_data_and_metric_id_output

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
