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





T = TypeVar("T", bound="ListBatchMetricsDataOutput")



@_attrs_define
class ListBatchMetricsDataOutput:
    """ 
        Attributes:
            batch_metrics_data (list[BatchMetricsData] | Unset):
            next_page_token (str | Unset):
     """

    batch_metrics_data: list[BatchMetricsData] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_metrics_data import BatchMetricsData
        batch_metrics_data: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.batch_metrics_data, Unset):
            batch_metrics_data = []
            for batch_metrics_data_item_data in self.batch_metrics_data:
                batch_metrics_data_item = batch_metrics_data_item_data.to_dict()
                batch_metrics_data.append(batch_metrics_data_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_metrics_data is not UNSET:
            field_dict["batchMetricsData"] = batch_metrics_data
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_metrics_data import BatchMetricsData
        d = dict(src_dict)
        batch_metrics_data = []
        _batch_metrics_data = d.pop("batchMetricsData", UNSET)
        for batch_metrics_data_item_data in (_batch_metrics_data or []):
            batch_metrics_data_item = BatchMetricsData.from_dict(batch_metrics_data_item_data)



            batch_metrics_data.append(batch_metrics_data_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_batch_metrics_data_output = cls(
            batch_metrics_data=batch_metrics_data,
            next_page_token=next_page_token,
        )


        list_batch_metrics_data_output.additional_properties = d
        return list_batch_metrics_data_output

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
