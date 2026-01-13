from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="DebugExperienceInput")



@_attrs_define
class DebugExperienceInput:
    """ 
        Attributes:
            batch_id (str | Unset):
            test_suite_id (str | Unset):
            build_id (str | Unset):
            containers (list[str] | Unset):
            pool_labels (list[str] | Unset):
     """

    batch_id: str | Unset = UNSET
    test_suite_id: str | Unset = UNSET
    build_id: str | Unset = UNSET
    containers: list[str] | Unset = UNSET
    pool_labels: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        batch_id = self.batch_id

        test_suite_id = self.test_suite_id

        build_id = self.build_id

        containers: list[str] | Unset = UNSET
        if not isinstance(self.containers, Unset):
            containers = self.containers



        pool_labels: list[str] | Unset = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if test_suite_id is not UNSET:
            field_dict["testSuiteID"] = test_suite_id
        if build_id is not UNSET:
            field_dict["buildID"] = build_id
        if containers is not UNSET:
            field_dict["containers"] = containers
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        batch_id = d.pop("batchID", UNSET)

        test_suite_id = d.pop("testSuiteID", UNSET)

        build_id = d.pop("buildID", UNSET)

        containers = cast(list[str], d.pop("containers", UNSET))


        pool_labels = cast(list[str], d.pop("poolLabels", UNSET))


        debug_experience_input = cls(
            batch_id=batch_id,
            test_suite_id=test_suite_id,
            build_id=build_id,
            containers=containers,
            pool_labels=pool_labels,
        )


        debug_experience_input.additional_properties = d
        return debug_experience_input

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
