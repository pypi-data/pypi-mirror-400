from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.workflow_suite_input import WorkflowSuiteInput





T = TypeVar("T", bound="CreateWorkflowInput")



@_attrs_define
class CreateWorkflowInput:
    """ 
        Attributes:
            name (str):
            description (str):
            workflow_suites (list[WorkflowSuiteInput]):
            ci_workflow_link (str | Unset):
     """

    name: str
    description: str
    workflow_suites: list[WorkflowSuiteInput]
    ci_workflow_link: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow_suite_input import WorkflowSuiteInput
        name = self.name

        description = self.description

        workflow_suites = []
        for workflow_suites_item_data in self.workflow_suites:
            workflow_suites_item = workflow_suites_item_data.to_dict()
            workflow_suites.append(workflow_suites_item)



        ci_workflow_link = self.ci_workflow_link


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "description": description,
            "workflowSuites": workflow_suites,
        })
        if ci_workflow_link is not UNSET:
            field_dict["ciWorkflowLink"] = ci_workflow_link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_suite_input import WorkflowSuiteInput
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        workflow_suites = []
        _workflow_suites = d.pop("workflowSuites")
        for workflow_suites_item_data in (_workflow_suites):
            workflow_suites_item = WorkflowSuiteInput.from_dict(workflow_suites_item_data)



            workflow_suites.append(workflow_suites_item)


        ci_workflow_link = d.pop("ciWorkflowLink", UNSET)

        create_workflow_input = cls(
            name=name,
            description=description,
            workflow_suites=workflow_suites,
            ci_workflow_link=ci_workflow_link,
        )


        create_workflow_input.additional_properties = d
        return create_workflow_input

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
