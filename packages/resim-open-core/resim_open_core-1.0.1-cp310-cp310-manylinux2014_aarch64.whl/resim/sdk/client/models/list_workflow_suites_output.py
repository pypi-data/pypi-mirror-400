from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.workflow_suite_output import WorkflowSuiteOutput





T = TypeVar("T", bound="ListWorkflowSuitesOutput")



@_attrs_define
class ListWorkflowSuitesOutput:
    """ 
        Attributes:
            workflow_suites (list[WorkflowSuiteOutput]):
     """

    workflow_suites: list[WorkflowSuiteOutput]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow_suite_output import WorkflowSuiteOutput
        workflow_suites = []
        for workflow_suites_item_data in self.workflow_suites:
            workflow_suites_item = workflow_suites_item_data.to_dict()
            workflow_suites.append(workflow_suites_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workflowSuites": workflow_suites,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_suite_output import WorkflowSuiteOutput
        d = dict(src_dict)
        workflow_suites = []
        _workflow_suites = d.pop("workflowSuites")
        for workflow_suites_item_data in (_workflow_suites):
            workflow_suites_item = WorkflowSuiteOutput.from_dict(workflow_suites_item_data)



            workflow_suites.append(workflow_suites_item)


        list_workflow_suites_output = cls(
            workflow_suites=workflow_suites,
        )


        list_workflow_suites_output.additional_properties = d
        return list_workflow_suites_output

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
