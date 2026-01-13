from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.metrics_data_type import MetricsDataType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="BatchMetricsData")



@_attrs_define
class BatchMetricsData:
    """ 
        Attributes:
            data_id (str | Unset):
            file_location (str | Unset):
            name (str | Unset):
            metrics_data_type (MetricsDataType | Unset):
            filename (None | str | Unset):
            org_id (str | Unset):
            user_id (str | Unset):
            metrics_data_url (str | Unset):
            creation_timestamp (datetime.datetime | Unset):
            batch_id (str | Unset):
     """

    data_id: str | Unset = UNSET
    file_location: str | Unset = UNSET
    name: str | Unset = UNSET
    metrics_data_type: MetricsDataType | Unset = UNSET
    filename: None | str | Unset = UNSET
    org_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    metrics_data_url: str | Unset = UNSET
    creation_timestamp: datetime.datetime | Unset = UNSET
    batch_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        data_id = self.data_id

        file_location = self.file_location

        name = self.name

        metrics_data_type: str | Unset = UNSET
        if not isinstance(self.metrics_data_type, Unset):
            metrics_data_type = self.metrics_data_type.value


        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        org_id = self.org_id

        user_id = self.user_id

        metrics_data_url = self.metrics_data_url

        creation_timestamp: str | Unset = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        batch_id = self.batch_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if data_id is not UNSET:
            field_dict["dataID"] = data_id
        if file_location is not UNSET:
            field_dict["fileLocation"] = file_location
        if name is not UNSET:
            field_dict["name"] = name
        if metrics_data_type is not UNSET:
            field_dict["metricsDataType"] = metrics_data_type
        if filename is not UNSET:
            field_dict["filename"] = filename
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if metrics_data_url is not UNSET:
            field_dict["metricsDataURL"] = metrics_data_url
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data_id = d.pop("dataID", UNSET)

        file_location = d.pop("fileLocation", UNSET)

        name = d.pop("name", UNSET)

        _metrics_data_type = d.pop("metricsDataType", UNSET)
        metrics_data_type: MetricsDataType | Unset
        if isinstance(_metrics_data_type,  Unset):
            metrics_data_type = UNSET
        else:
            metrics_data_type = MetricsDataType(_metrics_data_type)




        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))


        org_id = d.pop("orgID", UNSET)

        user_id = d.pop("userID", UNSET)

        metrics_data_url = d.pop("metricsDataURL", UNSET)

        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: datetime.datetime | Unset
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        batch_id = d.pop("batchID", UNSET)

        batch_metrics_data = cls(
            data_id=data_id,
            file_location=file_location,
            name=name,
            metrics_data_type=metrics_data_type,
            filename=filename,
            org_id=org_id,
            user_id=user_id,
            metrics_data_url=metrics_data_url,
            creation_timestamp=creation_timestamp,
            batch_id=batch_id,
        )


        batch_metrics_data.additional_properties = d
        return batch_metrics_data

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
