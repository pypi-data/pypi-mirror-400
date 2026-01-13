from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.report_log import ReportLog





T = TypeVar("T", bound="ListReportLogsOutput")



@_attrs_define
class ListReportLogsOutput:
    """ 
        Attributes:
            logs (list[ReportLog] | Unset):
            next_page_token (str | Unset):
     """

    logs: list[ReportLog] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.report_log import ReportLog
        logs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.logs, Unset):
            logs = []
            for logs_item_data in self.logs:
                logs_item = logs_item_data.to_dict()
                logs.append(logs_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if logs is not UNSET:
            field_dict["logs"] = logs
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_log import ReportLog
        d = dict(src_dict)
        logs = []
        _logs = d.pop("logs", UNSET)
        for logs_item_data in (_logs or []):
            logs_item = ReportLog.from_dict(logs_item_data)



            logs.append(logs_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_report_logs_output = cls(
            logs=logs,
            next_page_token=next_page_token,
        )


        list_report_logs_output.additional_properties = d
        return list_report_logs_output

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
