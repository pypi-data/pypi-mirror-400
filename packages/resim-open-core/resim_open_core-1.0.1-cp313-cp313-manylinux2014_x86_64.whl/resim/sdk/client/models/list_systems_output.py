from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.system import System





T = TypeVar("T", bound="ListSystemsOutput")



@_attrs_define
class ListSystemsOutput:
    """ 
        Attributes:
            systems (list[System] | Unset):
            next_page_token (str | Unset):
     """

    systems: list[System] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.system import System
        systems: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.systems, Unset):
            systems = []
            for systems_item_data in self.systems:
                systems_item = systems_item_data.to_dict()
                systems.append(systems_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if systems is not UNSET:
            field_dict["systems"] = systems
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.system import System
        d = dict(src_dict)
        systems = []
        _systems = d.pop("systems", UNSET)
        for systems_item_data in (_systems or []):
            systems_item = System.from_dict(systems_item_data)



            systems.append(systems_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_systems_output = cls(
            systems=systems,
            next_page_token=next_page_token,
        )


        list_systems_output.additional_properties = d
        return list_systems_output

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
