from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.batch import Batch





T = TypeVar("T", bound="ListBatchesOutput")



@_attrs_define
class ListBatchesOutput:
    """ 
        Attributes:
            batches (list[Batch] | Unset):
            next_page_token (str | Unset):
            total (int | Unset):
     """

    batches: list[Batch] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch import Batch
        batches: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.batches, Unset):
            batches = []
            for batches_item_data in self.batches:
                batches_item = batches_item_data.to_dict()
                batches.append(batches_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batches is not UNSET:
            field_dict["batches"] = batches
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch import Batch
        d = dict(src_dict)
        batches = []
        _batches = d.pop("batches", UNSET)
        for batches_item_data in (_batches or []):
            batches_item = Batch.from_dict(batches_item_data)



            batches.append(batches_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_batches_output = cls(
            batches=batches,
            next_page_token=next_page_token,
            total=total,
        )


        list_batches_output.additional_properties = d
        return list_batches_output

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
