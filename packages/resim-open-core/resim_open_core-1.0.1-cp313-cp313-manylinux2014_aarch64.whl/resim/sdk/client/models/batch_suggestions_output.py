from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.batch import Batch





T = TypeVar("T", bound="BatchSuggestionsOutput")



@_attrs_define
class BatchSuggestionsOutput:
    """ 
        Attributes:
            last_passing_on_main (Batch | None):
            latest_on_main (Batch | None):
            last_passing_on_branch (Batch | None):
            latest_on_branch (Batch | None):
     """

    last_passing_on_main: Batch | None
    latest_on_main: Batch | None
    last_passing_on_branch: Batch | None
    latest_on_branch: Batch | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch import Batch
        last_passing_on_main: dict[str, Any] | None
        if isinstance(self.last_passing_on_main, Batch):
            last_passing_on_main = self.last_passing_on_main.to_dict()
        else:
            last_passing_on_main = self.last_passing_on_main

        latest_on_main: dict[str, Any] | None
        if isinstance(self.latest_on_main, Batch):
            latest_on_main = self.latest_on_main.to_dict()
        else:
            latest_on_main = self.latest_on_main

        last_passing_on_branch: dict[str, Any] | None
        if isinstance(self.last_passing_on_branch, Batch):
            last_passing_on_branch = self.last_passing_on_branch.to_dict()
        else:
            last_passing_on_branch = self.last_passing_on_branch

        latest_on_branch: dict[str, Any] | None
        if isinstance(self.latest_on_branch, Batch):
            latest_on_branch = self.latest_on_branch.to_dict()
        else:
            latest_on_branch = self.latest_on_branch


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "lastPassingOnMain": last_passing_on_main,
            "latestOnMain": latest_on_main,
            "lastPassingOnBranch": last_passing_on_branch,
            "latestOnBranch": latest_on_branch,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch import Batch
        d = dict(src_dict)
        def _parse_last_passing_on_main(data: object) -> Batch | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_passing_on_main_type_1 = Batch.from_dict(data)



                return last_passing_on_main_type_1
            except: # noqa: E722
                pass
            return cast(Batch | None, data)

        last_passing_on_main = _parse_last_passing_on_main(d.pop("lastPassingOnMain"))


        def _parse_latest_on_main(data: object) -> Batch | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_on_main_type_1 = Batch.from_dict(data)



                return latest_on_main_type_1
            except: # noqa: E722
                pass
            return cast(Batch | None, data)

        latest_on_main = _parse_latest_on_main(d.pop("latestOnMain"))


        def _parse_last_passing_on_branch(data: object) -> Batch | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_passing_on_branch_type_1 = Batch.from_dict(data)



                return last_passing_on_branch_type_1
            except: # noqa: E722
                pass
            return cast(Batch | None, data)

        last_passing_on_branch = _parse_last_passing_on_branch(d.pop("lastPassingOnBranch"))


        def _parse_latest_on_branch(data: object) -> Batch | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_on_branch_type_1 = Batch.from_dict(data)



                return latest_on_branch_type_1
            except: # noqa: E722
                pass
            return cast(Batch | None, data)

        latest_on_branch = _parse_latest_on_branch(d.pop("latestOnBranch"))


        batch_suggestions_output = cls(
            last_passing_on_main=last_passing_on_main,
            latest_on_main=latest_on_main,
            last_passing_on_branch=last_passing_on_branch,
            latest_on_branch=latest_on_branch,
        )


        batch_suggestions_output.additional_properties = d
        return batch_suggestions_output

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
