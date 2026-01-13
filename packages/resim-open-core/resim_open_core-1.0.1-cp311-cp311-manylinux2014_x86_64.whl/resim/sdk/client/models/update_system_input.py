from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.architecture import Architecture
from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateSystemInput")



@_attrs_define
class UpdateSystemInput:
    """ 
        Attributes:
            name (str | Unset):
            description (str | Unset):
            build_vcpus (int | Unset):
            build_memory_mib (int | Unset):
            build_gpus (int | Unset):
            build_shared_memory_mb (int | Unset):
            architecture (Architecture | Unset):
            metrics_build_vcpus (int | Unset):
            metrics_build_memory_mib (int | Unset):
            metrics_build_gpus (int | Unset):
            metrics_build_shared_memory_mb (int | Unset):
     """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    build_vcpus: int | Unset = UNSET
    build_memory_mib: int | Unset = UNSET
    build_gpus: int | Unset = UNSET
    build_shared_memory_mb: int | Unset = UNSET
    architecture: Architecture | Unset = UNSET
    metrics_build_vcpus: int | Unset = UNSET
    metrics_build_memory_mib: int | Unset = UNSET
    metrics_build_gpus: int | Unset = UNSET
    metrics_build_shared_memory_mb: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        build_vcpus = self.build_vcpus

        build_memory_mib = self.build_memory_mib

        build_gpus = self.build_gpus

        build_shared_memory_mb = self.build_shared_memory_mb

        architecture: str | Unset = UNSET
        if not isinstance(self.architecture, Unset):
            architecture = self.architecture.value


        metrics_build_vcpus = self.metrics_build_vcpus

        metrics_build_memory_mib = self.metrics_build_memory_mib

        metrics_build_gpus = self.metrics_build_gpus

        metrics_build_shared_memory_mb = self.metrics_build_shared_memory_mb


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if build_vcpus is not UNSET:
            field_dict["build_vcpus"] = build_vcpus
        if build_memory_mib is not UNSET:
            field_dict["build_memory_mib"] = build_memory_mib
        if build_gpus is not UNSET:
            field_dict["build_gpus"] = build_gpus
        if build_shared_memory_mb is not UNSET:
            field_dict["build_shared_memory_mb"] = build_shared_memory_mb
        if architecture is not UNSET:
            field_dict["architecture"] = architecture
        if metrics_build_vcpus is not UNSET:
            field_dict["metrics_build_vcpus"] = metrics_build_vcpus
        if metrics_build_memory_mib is not UNSET:
            field_dict["metrics_build_memory_mib"] = metrics_build_memory_mib
        if metrics_build_gpus is not UNSET:
            field_dict["metrics_build_gpus"] = metrics_build_gpus
        if metrics_build_shared_memory_mb is not UNSET:
            field_dict["metrics_build_shared_memory_mb"] = metrics_build_shared_memory_mb

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        build_vcpus = d.pop("build_vcpus", UNSET)

        build_memory_mib = d.pop("build_memory_mib", UNSET)

        build_gpus = d.pop("build_gpus", UNSET)

        build_shared_memory_mb = d.pop("build_shared_memory_mb", UNSET)

        _architecture = d.pop("architecture", UNSET)
        architecture: Architecture | Unset
        if isinstance(_architecture,  Unset):
            architecture = UNSET
        else:
            architecture = Architecture(_architecture)




        metrics_build_vcpus = d.pop("metrics_build_vcpus", UNSET)

        metrics_build_memory_mib = d.pop("metrics_build_memory_mib", UNSET)

        metrics_build_gpus = d.pop("metrics_build_gpus", UNSET)

        metrics_build_shared_memory_mb = d.pop("metrics_build_shared_memory_mb", UNSET)

        update_system_input = cls(
            name=name,
            description=description,
            build_vcpus=build_vcpus,
            build_memory_mib=build_memory_mib,
            build_gpus=build_gpus,
            build_shared_memory_mb=build_shared_memory_mb,
            architecture=architecture,
            metrics_build_vcpus=metrics_build_vcpus,
            metrics_build_memory_mib=metrics_build_memory_mib,
            metrics_build_gpus=metrics_build_gpus,
            metrics_build_shared_memory_mb=metrics_build_shared_memory_mb,
        )


        update_system_input.additional_properties = d
        return update_system_input

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
