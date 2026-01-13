from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="UpdateWorkflowSuiteOutput")



@_attrs_define
class UpdateWorkflowSuiteOutput:
    """ 
        Attributes:
            test_suite_id (str):
            workflow_id (str):
            enabled (bool):
     """

    test_suite_id: str
    workflow_id: str
    enabled: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        test_suite_id = self.test_suite_id

        workflow_id = self.workflow_id

        enabled = self.enabled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "testSuiteID": test_suite_id,
            "workflowID": workflow_id,
            "enabled": enabled,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        test_suite_id = d.pop("testSuiteID")

        workflow_id = d.pop("workflowID")

        enabled = d.pop("enabled")

        update_workflow_suite_output = cls(
            test_suite_id=test_suite_id,
            workflow_id=workflow_id,
            enabled=enabled,
        )


        update_workflow_suite_output.additional_properties = d
        return update_workflow_suite_output

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
