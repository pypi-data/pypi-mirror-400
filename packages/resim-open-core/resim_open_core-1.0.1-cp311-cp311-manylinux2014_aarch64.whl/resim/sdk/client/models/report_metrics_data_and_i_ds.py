from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.metrics_data import MetricsData





T = TypeVar("T", bound="ReportMetricsDataAndIDs")



@_attrs_define
class ReportMetricsDataAndIDs:
    """ 
        Attributes:
            report_metric_id (str | Unset):
            report_metrics_data (MetricsData | Unset):
     """

    report_metric_id: str | Unset = UNSET
    report_metrics_data: MetricsData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.metrics_data import MetricsData
        report_metric_id = self.report_metric_id

        report_metrics_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.report_metrics_data, Unset):
            report_metrics_data = self.report_metrics_data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if report_metric_id is not UNSET:
            field_dict["reportMetricID"] = report_metric_id
        if report_metrics_data is not UNSET:
            field_dict["reportMetricsData"] = report_metrics_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metrics_data import MetricsData
        d = dict(src_dict)
        report_metric_id = d.pop("reportMetricID", UNSET)

        _report_metrics_data = d.pop("reportMetricsData", UNSET)
        report_metrics_data: MetricsData | Unset
        if isinstance(_report_metrics_data,  Unset):
            report_metrics_data = UNSET
        else:
            report_metrics_data = MetricsData.from_dict(_report_metrics_data)




        report_metrics_data_and_i_ds = cls(
            report_metric_id=report_metric_id,
            report_metrics_data=report_metrics_data,
        )


        report_metrics_data_and_i_ds.additional_properties = d
        return report_metrics_data_and_i_ds

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
