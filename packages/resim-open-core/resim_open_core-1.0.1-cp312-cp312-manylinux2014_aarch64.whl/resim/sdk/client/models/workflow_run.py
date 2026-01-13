from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.triggered_via import TriggeredVia
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.workflow_run_test_suite import WorkflowRunTestSuite





T = TypeVar("T", bound="WorkflowRun")



@_attrs_define
class WorkflowRun:
    """ 
        Attributes:
            workflow_run_id (str):
            workflow_id (str):
            creation_timestamp (datetime.datetime):
            build_id (str):
            user_id (str):
            org_id (str):
            workflow_run_test_suites (list[WorkflowRunTestSuite]):
            associated_account (str | Unset):
            triggered_via (TriggeredVia | Unset):
     """

    workflow_run_id: str
    workflow_id: str
    creation_timestamp: datetime.datetime
    build_id: str
    user_id: str
    org_id: str
    workflow_run_test_suites: list[WorkflowRunTestSuite]
    associated_account: str | Unset = UNSET
    triggered_via: TriggeredVia | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow_run_test_suite import WorkflowRunTestSuite
        workflow_run_id = self.workflow_run_id

        workflow_id = self.workflow_id

        creation_timestamp = self.creation_timestamp.isoformat()

        build_id = self.build_id

        user_id = self.user_id

        org_id = self.org_id

        workflow_run_test_suites = []
        for workflow_run_test_suites_item_data in self.workflow_run_test_suites:
            workflow_run_test_suites_item = workflow_run_test_suites_item_data.to_dict()
            workflow_run_test_suites.append(workflow_run_test_suites_item)



        associated_account = self.associated_account

        triggered_via: str | Unset = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workflowRunID": workflow_run_id,
            "workflowID": workflow_id,
            "creationTimestamp": creation_timestamp,
            "buildID": build_id,
            "userID": user_id,
            "orgID": org_id,
            "workflowRunTestSuites": workflow_run_test_suites,
        })
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_run_test_suite import WorkflowRunTestSuite
        d = dict(src_dict)
        workflow_run_id = d.pop("workflowRunID")

        workflow_id = d.pop("workflowID")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        build_id = d.pop("buildID")

        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        workflow_run_test_suites = []
        _workflow_run_test_suites = d.pop("workflowRunTestSuites")
        for workflow_run_test_suites_item_data in (_workflow_run_test_suites):
            workflow_run_test_suites_item = WorkflowRunTestSuite.from_dict(workflow_run_test_suites_item_data)



            workflow_run_test_suites.append(workflow_run_test_suites_item)


        associated_account = d.pop("associatedAccount", UNSET)

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: TriggeredVia | Unset
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        workflow_run = cls(
            workflow_run_id=workflow_run_id,
            workflow_id=workflow_id,
            creation_timestamp=creation_timestamp,
            build_id=build_id,
            user_id=user_id,
            org_id=org_id,
            workflow_run_test_suites=workflow_run_test_suites,
            associated_account=associated_account,
            triggered_via=triggered_via,
        )


        workflow_run.additional_properties = d
        return workflow_run

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
