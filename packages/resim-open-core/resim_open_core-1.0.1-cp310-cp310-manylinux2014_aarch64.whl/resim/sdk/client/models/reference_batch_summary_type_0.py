from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ReferenceBatchSummaryType0")



@_attrs_define
class ReferenceBatchSummaryType0:
    """ 
        Attributes:
            fixed_tests (int):
            new_tests (int):
            new_issues (int):
     """

    fixed_tests: int
    new_tests: int
    new_issues: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        fixed_tests = self.fixed_tests

        new_tests = self.new_tests

        new_issues = self.new_issues


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "fixedTests": fixed_tests,
            "newTests": new_tests,
            "newIssues": new_issues,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fixed_tests = d.pop("fixedTests")

        new_tests = d.pop("newTests")

        new_issues = d.pop("newIssues")

        reference_batch_summary_type_0 = cls(
            fixed_tests=fixed_tests,
            new_tests=new_tests,
            new_issues=new_issues,
        )


        reference_batch_summary_type_0.additional_properties = d
        return reference_batch_summary_type_0

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
