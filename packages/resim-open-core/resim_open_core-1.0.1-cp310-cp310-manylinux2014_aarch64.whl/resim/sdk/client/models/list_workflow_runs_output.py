from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.workflow_run import WorkflowRun





T = TypeVar("T", bound="ListWorkflowRunsOutput")



@_attrs_define
class ListWorkflowRunsOutput:
    """ 
        Attributes:
            workflow_runs (list[WorkflowRun]):
            next_page_token (str):
            total (int):
     """

    workflow_runs: list[WorkflowRun]
    next_page_token: str
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow_run import WorkflowRun
        workflow_runs = []
        for workflow_runs_item_data in self.workflow_runs:
            workflow_runs_item = workflow_runs_item_data.to_dict()
            workflow_runs.append(workflow_runs_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workflowRuns": workflow_runs,
            "nextPageToken": next_page_token,
            "total": total,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_run import WorkflowRun
        d = dict(src_dict)
        workflow_runs = []
        _workflow_runs = d.pop("workflowRuns")
        for workflow_runs_item_data in (_workflow_runs):
            workflow_runs_item = WorkflowRun.from_dict(workflow_runs_item_data)



            workflow_runs.append(workflow_runs_item)


        next_page_token = d.pop("nextPageToken")

        total = d.pop("total")

        list_workflow_runs_output = cls(
            workflow_runs=workflow_runs,
            next_page_token=next_page_token,
            total=total,
        )


        list_workflow_runs_output.additional_properties = d
        return list_workflow_runs_output

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
