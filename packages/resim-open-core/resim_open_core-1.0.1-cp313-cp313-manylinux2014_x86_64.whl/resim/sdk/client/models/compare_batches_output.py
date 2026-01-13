from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.compare_batch_test import CompareBatchTest





T = TypeVar("T", bound="CompareBatchesOutput")



@_attrs_define
class CompareBatchesOutput:
    """ 
        Attributes:
            total (int):
            next_page_token (str):
            tests (list[CompareBatchTest]):
     """

    total: int
    next_page_token: str
    tests: list[CompareBatchTest]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.compare_batch_test import CompareBatchTest
        total = self.total

        next_page_token = self.next_page_token

        tests = []
        for tests_item_data in self.tests:
            tests_item = tests_item_data.to_dict()
            tests.append(tests_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "total": total,
            "nextPageToken": next_page_token,
            "tests": tests,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compare_batch_test import CompareBatchTest
        d = dict(src_dict)
        total = d.pop("total")

        next_page_token = d.pop("nextPageToken")

        tests = []
        _tests = d.pop("tests")
        for tests_item_data in (_tests):
            tests_item = CompareBatchTest.from_dict(tests_item_data)



            tests.append(tests_item)


        compare_batches_output = cls(
            total=total,
            next_page_token=next_page_token,
            tests=tests,
        )


        compare_batches_output.additional_properties = d
        return compare_batches_output

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
