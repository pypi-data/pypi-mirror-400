from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.conflated_job_status import ConflatedJobStatus
from typing import cast






T = TypeVar("T", bound="CompareBatchTestDetailsType0")



@_attrs_define
class CompareBatchTestDetailsType0:
    """ 
        Attributes:
            job_id (str):
            status (ConflatedJobStatus):
            num_metrics (int | None): The number of failblock/failwarn/passing metrics (based on job's status). Otherwise
                this will be null
     """

    job_id: str
    status: ConflatedJobStatus
    num_metrics: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        status = self.status.value

        num_metrics: int | None
        num_metrics = self.num_metrics


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "jobID": job_id,
            "status": status,
            "numMetrics": num_metrics,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("jobID")

        status = ConflatedJobStatus(d.pop("status"))




        def _parse_num_metrics(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        num_metrics = _parse_num_metrics(d.pop("numMetrics"))


        compare_batch_test_details_type_0 = cls(
            job_id=job_id,
            status=status,
            num_metrics=num_metrics,
        )


        compare_batch_test_details_type_0.additional_properties = d
        return compare_batch_test_details_type_0

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
