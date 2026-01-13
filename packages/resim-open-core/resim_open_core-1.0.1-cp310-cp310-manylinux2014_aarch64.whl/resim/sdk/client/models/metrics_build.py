from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="MetricsBuild")



@_attrs_define
class MetricsBuild:
    """ 
        Attributes:
            metrics_build_id (str):
            project_id (str):
            name (str):
            version (str):
            image_uri (str):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
     """

    metrics_build_id: str
    project_id: str
    name: str
    version: str
    image_uri: str
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        metrics_build_id = self.metrics_build_id

        project_id = self.project_id

        name = self.name

        version = self.version

        image_uri = self.image_uri

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "metricsBuildID": metrics_build_id,
            "projectID": project_id,
            "name": name,
            "version": version,
            "imageUri": image_uri,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        metrics_build_id = d.pop("metricsBuildID")

        project_id = d.pop("projectID")

        name = d.pop("name")

        version = d.pop("version")

        image_uri = d.pop("imageUri")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        metrics_build = cls(
            metrics_build_id=metrics_build_id,
            project_id=project_id,
            name=name,
            version=version,
            image_uri=image_uri,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
        )


        metrics_build.additional_properties = d
        return metrics_build

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
