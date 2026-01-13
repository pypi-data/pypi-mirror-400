from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.metric_status import MetricStatus
from ..models.metric_type import MetricType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Metric")



@_attrs_define
class Metric:
    """ 
        Attributes:
            metric_id (str | Unset):
            name (str | Unset):
            creation_timestamp (datetime.datetime | Unset):
            file_location (str | Unset):
            user_id (str | Unset):
            org_id (str | Unset):
            status (MetricStatus | Unset):
            type_ (MetricType | Unset):
            data_i_ds (list[str] | Unset):
            value (float | None | Unset):
            unit (None | str | Unset):
            event_metric (bool | Unset): true if this metric is for an event
            project_id (str | Unset):
            metric_url (str | Unset):
     """

    metric_id: str | Unset = UNSET
    name: str | Unset = UNSET
    creation_timestamp: datetime.datetime | Unset = UNSET
    file_location: str | Unset = UNSET
    user_id: str | Unset = UNSET
    org_id: str | Unset = UNSET
    status: MetricStatus | Unset = UNSET
    type_: MetricType | Unset = UNSET
    data_i_ds: list[str] | Unset = UNSET
    value: float | None | Unset = UNSET
    unit: None | str | Unset = UNSET
    event_metric: bool | Unset = UNSET
    project_id: str | Unset = UNSET
    metric_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        metric_id = self.metric_id

        name = self.name

        creation_timestamp: str | Unset = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        file_location = self.file_location

        user_id = self.user_id

        org_id = self.org_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        data_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.data_i_ds, Unset):
            data_i_ds = self.data_i_ds



        value: float | None | Unset
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        unit: None | str | Unset
        if isinstance(self.unit, Unset):
            unit = UNSET
        else:
            unit = self.unit

        event_metric = self.event_metric

        project_id = self.project_id

        metric_url = self.metric_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if metric_id is not UNSET:
            field_dict["metricID"] = metric_id
        if name is not UNSET:
            field_dict["name"] = name
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if file_location is not UNSET:
            field_dict["fileLocation"] = file_location
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if status is not UNSET:
            field_dict["status"] = status
        if type_ is not UNSET:
            field_dict["type"] = type_
        if data_i_ds is not UNSET:
            field_dict["dataIDs"] = data_i_ds
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit
        if event_metric is not UNSET:
            field_dict["eventMetric"] = event_metric
        if project_id is not UNSET:
            field_dict["projectID"] = project_id
        if metric_url is not UNSET:
            field_dict["metricURL"] = metric_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        metric_id = d.pop("metricID", UNSET)

        name = d.pop("name", UNSET)

        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: datetime.datetime | Unset
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        file_location = d.pop("fileLocation", UNSET)

        user_id = d.pop("userID", UNSET)

        org_id = d.pop("orgID", UNSET)

        _status = d.pop("status", UNSET)
        status: MetricStatus | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = MetricStatus(_status)




        _type_ = d.pop("type", UNSET)
        type_: MetricType | Unset
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = MetricType(_type_)




        data_i_ds = cast(list[str], d.pop("dataIDs", UNSET))


        def _parse_value(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        value = _parse_value(d.pop("value", UNSET))


        def _parse_unit(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        unit = _parse_unit(d.pop("unit", UNSET))


        event_metric = d.pop("eventMetric", UNSET)

        project_id = d.pop("projectID", UNSET)

        metric_url = d.pop("metricURL", UNSET)

        metric = cls(
            metric_id=metric_id,
            name=name,
            creation_timestamp=creation_timestamp,
            file_location=file_location,
            user_id=user_id,
            org_id=org_id,
            status=status,
            type_=type_,
            data_i_ds=data_i_ds,
            value=value,
            unit=unit,
            event_metric=event_metric,
            project_id=project_id,
            metric_url=metric_url,
        )


        metric.additional_properties = d
        return metric

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
