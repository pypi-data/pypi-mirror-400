from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Workflow")



@_attrs_define
class Workflow:
    """ 
        Attributes:
            workflow_id (str):
            project_id (str):
            name (str):
            description (str):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
            archived (bool):
            ci_workflow_link (None | str | Unset):
            update_timestamp (datetime.datetime | Unset):
            last_run_timestamp (datetime.datetime | Unset):
     """

    workflow_id: str
    project_id: str
    name: str
    description: str
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    archived: bool
    ci_workflow_link: None | str | Unset = UNSET
    update_timestamp: datetime.datetime | Unset = UNSET
    last_run_timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        workflow_id = self.workflow_id

        project_id = self.project_id

        name = self.name

        description = self.description

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id

        archived = self.archived

        ci_workflow_link: None | str | Unset
        if isinstance(self.ci_workflow_link, Unset):
            ci_workflow_link = UNSET
        else:
            ci_workflow_link = self.ci_workflow_link

        update_timestamp: str | Unset = UNSET
        if not isinstance(self.update_timestamp, Unset):
            update_timestamp = self.update_timestamp.isoformat()

        last_run_timestamp: str | Unset = UNSET
        if not isinstance(self.last_run_timestamp, Unset):
            last_run_timestamp = self.last_run_timestamp.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workflowID": workflow_id,
            "projectID": project_id,
            "name": name,
            "description": description,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
            "archived": archived,
        })
        if ci_workflow_link is not UNSET:
            field_dict["ciWorkflowLink"] = ci_workflow_link
        if update_timestamp is not UNSET:
            field_dict["updateTimestamp"] = update_timestamp
        if last_run_timestamp is not UNSET:
            field_dict["lastRunTimestamp"] = last_run_timestamp

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        workflow_id = d.pop("workflowID")

        project_id = d.pop("projectID")

        name = d.pop("name")

        description = d.pop("description")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        archived = d.pop("archived")

        def _parse_ci_workflow_link(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ci_workflow_link = _parse_ci_workflow_link(d.pop("ciWorkflowLink", UNSET))


        _update_timestamp = d.pop("updateTimestamp", UNSET)
        update_timestamp: datetime.datetime | Unset
        if isinstance(_update_timestamp,  Unset):
            update_timestamp = UNSET
        else:
            update_timestamp = isoparse(_update_timestamp)




        _last_run_timestamp = d.pop("lastRunTimestamp", UNSET)
        last_run_timestamp: datetime.datetime | Unset
        if isinstance(_last_run_timestamp,  Unset):
            last_run_timestamp = UNSET
        else:
            last_run_timestamp = isoparse(_last_run_timestamp)




        workflow = cls(
            workflow_id=workflow_id,
            project_id=project_id,
            name=name,
            description=description,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
            archived=archived,
            ci_workflow_link=ci_workflow_link,
            update_timestamp=update_timestamp,
            last_run_timestamp=last_run_timestamp,
        )


        workflow.additional_properties = d
        return workflow

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
