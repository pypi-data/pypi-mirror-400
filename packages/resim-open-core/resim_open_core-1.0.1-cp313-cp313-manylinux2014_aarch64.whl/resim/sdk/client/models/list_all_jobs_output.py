from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.job import Job





T = TypeVar("T", bound="ListAllJobsOutput")



@_attrs_define
class ListAllJobsOutput:
    """ 
        Attributes:
            jobs (list[Job] | Unset):
            next_page_token (str | Unset):
            total (int | Unset):
     """

    jobs: list[Job] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.job import Job
        jobs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.jobs, Unset):
            jobs = []
            for jobs_item_data in self.jobs:
                jobs_item = jobs_item_data.to_dict()
                jobs.append(jobs_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if jobs is not UNSET:
            field_dict["jobs"] = jobs
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job import Job
        d = dict(src_dict)
        jobs = []
        _jobs = d.pop("jobs", UNSET)
        for jobs_item_data in (_jobs or []):
            jobs_item = Job.from_dict(jobs_item_data)



            jobs.append(jobs_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_all_jobs_output = cls(
            jobs=jobs,
            next_page_token=next_page_token,
            total=total,
        )


        list_all_jobs_output.additional_properties = d
        return list_all_jobs_output

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
