from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.architecture import Architecture
from ..types import UNSET, Unset






T = TypeVar("T", bound="CreateSystemInput")



@_attrs_define
class CreateSystemInput:
    """ 
        Attributes:
            name (str):
            description (str):
            build_vcpus (int):
            build_memory_mib (int):
            build_gpus (int):
            build_shared_memory_mb (int):
            metrics_build_vcpus (int):
            metrics_build_memory_mib (int):
            metrics_build_gpus (int):
            metrics_build_shared_memory_mb (int):
            architecture (Architecture | Unset):
     """

    name: str
    description: str
    build_vcpus: int
    build_memory_mib: int
    build_gpus: int
    build_shared_memory_mb: int
    metrics_build_vcpus: int
    metrics_build_memory_mib: int
    metrics_build_gpus: int
    metrics_build_shared_memory_mb: int
    architecture: Architecture | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        build_vcpus = self.build_vcpus

        build_memory_mib = self.build_memory_mib

        build_gpus = self.build_gpus

        build_shared_memory_mb = self.build_shared_memory_mb

        metrics_build_vcpus = self.metrics_build_vcpus

        metrics_build_memory_mib = self.metrics_build_memory_mib

        metrics_build_gpus = self.metrics_build_gpus

        metrics_build_shared_memory_mb = self.metrics_build_shared_memory_mb

        architecture: str | Unset = UNSET
        if not isinstance(self.architecture, Unset):
            architecture = self.architecture.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "description": description,
            "build_vcpus": build_vcpus,
            "build_memory_mib": build_memory_mib,
            "build_gpus": build_gpus,
            "build_shared_memory_mb": build_shared_memory_mb,
            "metrics_build_vcpus": metrics_build_vcpus,
            "metrics_build_memory_mib": metrics_build_memory_mib,
            "metrics_build_gpus": metrics_build_gpus,
            "metrics_build_shared_memory_mb": metrics_build_shared_memory_mb,
        })
        if architecture is not UNSET:
            field_dict["architecture"] = architecture

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        build_vcpus = d.pop("build_vcpus")

        build_memory_mib = d.pop("build_memory_mib")

        build_gpus = d.pop("build_gpus")

        build_shared_memory_mb = d.pop("build_shared_memory_mb")

        metrics_build_vcpus = d.pop("metrics_build_vcpus")

        metrics_build_memory_mib = d.pop("metrics_build_memory_mib")

        metrics_build_gpus = d.pop("metrics_build_gpus")

        metrics_build_shared_memory_mb = d.pop("metrics_build_shared_memory_mb")

        _architecture = d.pop("architecture", UNSET)
        architecture: Architecture | Unset
        if isinstance(_architecture,  Unset):
            architecture = UNSET
        else:
            architecture = Architecture(_architecture)




        create_system_input = cls(
            name=name,
            description=description,
            build_vcpus=build_vcpus,
            build_memory_mib=build_memory_mib,
            build_gpus=build_gpus,
            build_shared_memory_mb=build_shared_memory_mb,
            metrics_build_vcpus=metrics_build_vcpus,
            metrics_build_memory_mib=metrics_build_memory_mib,
            metrics_build_gpus=metrics_build_gpus,
            metrics_build_shared_memory_mb=metrics_build_shared_memory_mb,
            architecture=architecture,
        )


        create_system_input.additional_properties = d
        return create_system_input

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
