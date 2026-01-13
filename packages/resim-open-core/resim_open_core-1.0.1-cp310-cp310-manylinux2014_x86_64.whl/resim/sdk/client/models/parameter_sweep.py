from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.parameter_sweep_status import ParameterSweepStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.sweep_parameter import SweepParameter
  from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType





T = TypeVar("T", bound="ParameterSweep")



@_attrs_define
class ParameterSweep:
    """ 
        Attributes:
            associated_account (str):
            parameter_sweep_id (str | Unset):
            project_id (str | Unset):
            name (str | Unset):
            status (ParameterSweepStatus | Unset):
            status_history (list[ParameterSweepStatusHistoryType] | Unset):
            last_updated_timestamp (datetime.datetime | Unset):
            creation_timestamp (datetime.datetime | Unset):
            parameters (list[SweepParameter] | Unset):
            batches (list[str] | Unset):
            batch_friendly_names (list[str] | Unset):
            user_id (str | Unset):
            org_id (str | Unset):
     """

    associated_account: str
    parameter_sweep_id: str | Unset = UNSET
    project_id: str | Unset = UNSET
    name: str | Unset = UNSET
    status: ParameterSweepStatus | Unset = UNSET
    status_history: list[ParameterSweepStatusHistoryType] | Unset = UNSET
    last_updated_timestamp: datetime.datetime | Unset = UNSET
    creation_timestamp: datetime.datetime | Unset = UNSET
    parameters: list[SweepParameter] | Unset = UNSET
    batches: list[str] | Unset = UNSET
    batch_friendly_names: list[str] | Unset = UNSET
    user_id: str | Unset = UNSET
    org_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.sweep_parameter import SweepParameter
        from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType
        associated_account = self.associated_account

        parameter_sweep_id = self.parameter_sweep_id

        project_id = self.project_id

        name = self.name

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        status_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.status_history, Unset):
            status_history = []
            for componentsschemasparameter_sweep_status_history_item_data in self.status_history:
                componentsschemasparameter_sweep_status_history_item = componentsschemasparameter_sweep_status_history_item_data.to_dict()
                status_history.append(componentsschemasparameter_sweep_status_history_item)



        last_updated_timestamp: str | Unset = UNSET
        if not isinstance(self.last_updated_timestamp, Unset):
            last_updated_timestamp = self.last_updated_timestamp.isoformat()

        creation_timestamp: str | Unset = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)



        batches: list[str] | Unset = UNSET
        if not isinstance(self.batches, Unset):
            batches = self.batches



        batch_friendly_names: list[str] | Unset = UNSET
        if not isinstance(self.batch_friendly_names, Unset):
            batch_friendly_names = self.batch_friendly_names



        user_id = self.user_id

        org_id = self.org_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "associatedAccount": associated_account,
        })
        if parameter_sweep_id is not UNSET:
            field_dict["parameterSweepID"] = parameter_sweep_id
        if project_id is not UNSET:
            field_dict["projectID"] = project_id
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if status_history is not UNSET:
            field_dict["statusHistory"] = status_history
        if last_updated_timestamp is not UNSET:
            field_dict["lastUpdatedTimestamp"] = last_updated_timestamp
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if batches is not UNSET:
            field_dict["batches"] = batches
        if batch_friendly_names is not UNSET:
            field_dict["batchFriendlyNames"] = batch_friendly_names
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if org_id is not UNSET:
            field_dict["orgID"] = org_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sweep_parameter import SweepParameter
        from ..models.parameter_sweep_status_history_type import ParameterSweepStatusHistoryType
        d = dict(src_dict)
        associated_account = d.pop("associatedAccount")

        parameter_sweep_id = d.pop("parameterSweepID", UNSET)

        project_id = d.pop("projectID", UNSET)

        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: ParameterSweepStatus | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ParameterSweepStatus(_status)




        status_history = []
        _status_history = d.pop("statusHistory", UNSET)
        for componentsschemasparameter_sweep_status_history_item_data in (_status_history or []):
            componentsschemasparameter_sweep_status_history_item = ParameterSweepStatusHistoryType.from_dict(componentsschemasparameter_sweep_status_history_item_data)



            status_history.append(componentsschemasparameter_sweep_status_history_item)


        _last_updated_timestamp = d.pop("lastUpdatedTimestamp", UNSET)
        last_updated_timestamp: datetime.datetime | Unset
        if isinstance(_last_updated_timestamp,  Unset):
            last_updated_timestamp = UNSET
        else:
            last_updated_timestamp = isoparse(_last_updated_timestamp)




        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: datetime.datetime | Unset
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        parameters = []
        _parameters = d.pop("parameters", UNSET)
        for parameters_item_data in (_parameters or []):
            parameters_item = SweepParameter.from_dict(parameters_item_data)



            parameters.append(parameters_item)


        batches = cast(list[str], d.pop("batches", UNSET))


        batch_friendly_names = cast(list[str], d.pop("batchFriendlyNames", UNSET))


        user_id = d.pop("userID", UNSET)

        org_id = d.pop("orgID", UNSET)

        parameter_sweep = cls(
            associated_account=associated_account,
            parameter_sweep_id=parameter_sweep_id,
            project_id=project_id,
            name=name,
            status=status,
            status_history=status_history,
            last_updated_timestamp=last_updated_timestamp,
            creation_timestamp=creation_timestamp,
            parameters=parameters,
            batches=batches,
            batch_friendly_names=batch_friendly_names,
            user_id=user_id,
            org_id=org_id,
        )


        parameter_sweep.additional_properties = d
        return parameter_sweep

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
