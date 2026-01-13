from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.test_suite_summary import TestSuiteSummary





T = TypeVar("T", bound="TestSuiteSummaryOutput")



@_attrs_define
class TestSuiteSummaryOutput:
    """ 
        Attributes:
            test_suites (list[TestSuiteSummary]):
            next_page_token (str):
     """

    test_suites: list[TestSuiteSummary]
    next_page_token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.test_suite_summary import TestSuiteSummary
        test_suites = []
        for test_suites_item_data in self.test_suites:
            test_suites_item = test_suites_item_data.to_dict()
            test_suites.append(test_suites_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "testSuites": test_suites,
            "nextPageToken": next_page_token,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_suite_summary import TestSuiteSummary
        d = dict(src_dict)
        test_suites = []
        _test_suites = d.pop("testSuites")
        for test_suites_item_data in (_test_suites):
            test_suites_item = TestSuiteSummary.from_dict(test_suites_item_data)



            test_suites.append(test_suites_item)


        next_page_token = d.pop("nextPageToken")

        test_suite_summary_output = cls(
            test_suites=test_suites,
            next_page_token=next_page_token,
        )


        test_suite_summary_output.additional_properties = d
        return test_suite_summary_output

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
