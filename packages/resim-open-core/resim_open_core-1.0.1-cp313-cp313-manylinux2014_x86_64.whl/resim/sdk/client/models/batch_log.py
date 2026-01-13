from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.execution_step import ExecutionStep
from ..models.log_type import LogType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="BatchLog")



@_attrs_define
class BatchLog:
    """ 
        Attributes:
            log_id (str | Unset):
            file_name (str | Unset):
            file_size (int | Unset):
            checksum (str | Unset):
            creation_timestamp (datetime.datetime | Unset):
            location (str | Unset):
            log_output_location (str | Unset):
            execution_step (ExecutionStep | Unset):
            log_type (LogType | Unset):
            user_id (str | Unset):
            org_id (str | Unset):
            batch_id (str | Unset):
     """

    log_id: str | Unset = UNSET
    file_name: str | Unset = UNSET
    file_size: int | Unset = UNSET
    checksum: str | Unset = UNSET
    creation_timestamp: datetime.datetime | Unset = UNSET
    location: str | Unset = UNSET
    log_output_location: str | Unset = UNSET
    execution_step: ExecutionStep | Unset = UNSET
    log_type: LogType | Unset = UNSET
    user_id: str | Unset = UNSET
    org_id: str | Unset = UNSET
    batch_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        log_id = self.log_id

        file_name = self.file_name

        file_size = self.file_size

        checksum = self.checksum

        creation_timestamp: str | Unset = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        location = self.location

        log_output_location = self.log_output_location

        execution_step: str | Unset = UNSET
        if not isinstance(self.execution_step, Unset):
            execution_step = self.execution_step.value


        log_type: str | Unset = UNSET
        if not isinstance(self.log_type, Unset):
            log_type = self.log_type.value


        user_id = self.user_id

        org_id = self.org_id

        batch_id = self.batch_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if log_id is not UNSET:
            field_dict["logID"] = log_id
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if file_size is not UNSET:
            field_dict["fileSize"] = file_size
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if location is not UNSET:
            field_dict["location"] = location
        if log_output_location is not UNSET:
            field_dict["logOutputLocation"] = log_output_location
        if execution_step is not UNSET:
            field_dict["executionStep"] = execution_step
        if log_type is not UNSET:
            field_dict["logType"] = log_type
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        log_id = d.pop("logID", UNSET)

        file_name = d.pop("fileName", UNSET)

        file_size = d.pop("fileSize", UNSET)

        checksum = d.pop("checksum", UNSET)

        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: datetime.datetime | Unset
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        location = d.pop("location", UNSET)

        log_output_location = d.pop("logOutputLocation", UNSET)

        _execution_step = d.pop("executionStep", UNSET)
        execution_step: ExecutionStep | Unset
        if isinstance(_execution_step,  Unset):
            execution_step = UNSET
        else:
            execution_step = ExecutionStep(_execution_step)




        _log_type = d.pop("logType", UNSET)
        log_type: LogType | Unset
        if isinstance(_log_type,  Unset):
            log_type = UNSET
        else:
            log_type = LogType(_log_type)




        user_id = d.pop("userID", UNSET)

        org_id = d.pop("orgID", UNSET)

        batch_id = d.pop("batchID", UNSET)

        batch_log = cls(
            log_id=log_id,
            file_name=file_name,
            file_size=file_size,
            checksum=checksum,
            creation_timestamp=creation_timestamp,
            location=location,
            log_output_location=log_output_location,
            execution_step=execution_step,
            log_type=log_type,
            user_id=user_id,
            org_id=org_id,
            batch_id=batch_id,
        )


        batch_log.additional_properties = d
        return batch_log

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
