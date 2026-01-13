from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.workflow import Workflow





T = TypeVar("T", bound="ListWorkflowsOutput")



@_attrs_define
class ListWorkflowsOutput:
    """ 
        Attributes:
            workflows (list[Workflow]):
            next_page_token (str):
            total (int):
     """

    workflows: list[Workflow]
    next_page_token: str
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow import Workflow
        workflows = []
        for workflows_item_data in self.workflows:
            workflows_item = workflows_item_data.to_dict()
            workflows.append(workflows_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workflows": workflows,
            "nextPageToken": next_page_token,
            "total": total,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow import Workflow
        d = dict(src_dict)
        workflows = []
        _workflows = d.pop("workflows")
        for workflows_item_data in (_workflows):
            workflows_item = Workflow.from_dict(workflows_item_data)



            workflows.append(workflows_item)


        next_page_token = d.pop("nextPageToken")

        total = d.pop("total")

        list_workflows_output = cls(
            workflows=workflows,
            next_page_token=next_page_token,
            total=total,
        )


        list_workflows_output.additional_properties = d
        return list_workflows_output

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
