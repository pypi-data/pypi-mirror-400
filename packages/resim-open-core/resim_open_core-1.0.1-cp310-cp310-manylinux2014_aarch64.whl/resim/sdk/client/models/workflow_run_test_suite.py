from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="WorkflowRunTestSuite")



@_attrs_define
class WorkflowRunTestSuite:
    """ 
        Attributes:
            batch_id (str):
            test_suite_id (str):
     """

    batch_id: str
    test_suite_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        batch_id = self.batch_id

        test_suite_id = self.test_suite_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "batchID": batch_id,
            "testSuiteID": test_suite_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        batch_id = d.pop("batchID")

        test_suite_id = d.pop("testSuiteID")

        workflow_run_test_suite = cls(
            batch_id=batch_id,
            test_suite_id=test_suite_id,
        )


        workflow_run_test_suite.additional_properties = d
        return workflow_run_test_suite

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
