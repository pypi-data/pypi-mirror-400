from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.report import Report





T = TypeVar("T", bound="ListReportsOutput")



@_attrs_define
class ListReportsOutput:
    """ 
        Attributes:
            reports (list[Report] | Unset):
            next_page_token (str | Unset):
            total (int | Unset):
     """

    reports: list[Report] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.report import Report
        reports: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.reports, Unset):
            reports = []
            for reports_item_data in self.reports:
                reports_item = reports_item_data.to_dict()
                reports.append(reports_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if reports is not UNSET:
            field_dict["reports"] = reports
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report import Report
        d = dict(src_dict)
        reports = []
        _reports = d.pop("reports", UNSET)
        for reports_item_data in (_reports or []):
            reports_item = Report.from_dict(reports_item_data)



            reports.append(reports_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_reports_output = cls(
            reports=reports,
            next_page_token=next_page_token,
            total=total,
        )


        list_reports_output.additional_properties = d
        return list_reports_output

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
