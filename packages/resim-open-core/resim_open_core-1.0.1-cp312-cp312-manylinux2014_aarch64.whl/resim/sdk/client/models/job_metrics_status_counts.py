from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="JobMetricsStatusCounts")



@_attrs_define
class JobMetricsStatusCounts:
    """ 
        Attributes:
            passed (int):
            raw (int):
            no_status_reported (int):
            not_applicable (int):
            fail_warn (int):
            fail_block (int):
     """

    passed: int
    raw: int
    no_status_reported: int
    not_applicable: int
    fail_warn: int
    fail_block: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        passed = self.passed

        raw = self.raw

        no_status_reported = self.no_status_reported

        not_applicable = self.not_applicable

        fail_warn = self.fail_warn

        fail_block = self.fail_block


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "passed": passed,
            "raw": raw,
            "noStatusReported": no_status_reported,
            "notApplicable": not_applicable,
            "failWarn": fail_warn,
            "failBlock": fail_block,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        passed = d.pop("passed")

        raw = d.pop("raw")

        no_status_reported = d.pop("noStatusReported")

        not_applicable = d.pop("notApplicable")

        fail_warn = d.pop("failWarn")

        fail_block = d.pop("failBlock")

        job_metrics_status_counts = cls(
            passed=passed,
            raw=raw,
            no_status_reported=no_status_reported,
            not_applicable=not_applicable,
            fail_warn=fail_warn,
            fail_block=fail_block,
        )


        job_metrics_status_counts.additional_properties = d
        return job_metrics_status_counts

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
