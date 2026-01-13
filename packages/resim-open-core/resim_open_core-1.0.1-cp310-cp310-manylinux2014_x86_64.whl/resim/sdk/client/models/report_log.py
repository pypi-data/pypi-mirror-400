from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.log_type import LogType
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="ReportLog")



@_attrs_define
class ReportLog:
    """ 
        Attributes:
            log_id (str):
            file_name (str):
            file_size (int):
            checksum (str):
            creation_timestamp (datetime.datetime):
            location (str):
            log_output_location (str):
            log_type (LogType):
            user_id (str):
            org_id (str):
     """

    log_id: str
    file_name: str
    file_size: int
    checksum: str
    creation_timestamp: datetime.datetime
    location: str
    log_output_location: str
    log_type: LogType
    user_id: str
    org_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        log_id = self.log_id

        file_name = self.file_name

        file_size = self.file_size

        checksum = self.checksum

        creation_timestamp = self.creation_timestamp.isoformat()

        location = self.location

        log_output_location = self.log_output_location

        log_type = self.log_type.value

        user_id = self.user_id

        org_id = self.org_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "logID": log_id,
            "fileName": file_name,
            "fileSize": file_size,
            "checksum": checksum,
            "creationTimestamp": creation_timestamp,
            "location": location,
            "logOutputLocation": log_output_location,
            "logType": log_type,
            "userID": user_id,
            "orgID": org_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        log_id = d.pop("logID")

        file_name = d.pop("fileName")

        file_size = d.pop("fileSize")

        checksum = d.pop("checksum")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        location = d.pop("location")

        log_output_location = d.pop("logOutputLocation")

        log_type = LogType(d.pop("logType"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        report_log = cls(
            log_id=log_id,
            file_name=file_name,
            file_size=file_size,
            checksum=checksum,
            creation_timestamp=creation_timestamp,
            location=location,
            log_output_location=log_output_location,
            log_type=log_type,
            user_id=user_id,
            org_id=org_id,
        )


        report_log.additional_properties = d
        return report_log

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
