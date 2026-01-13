from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.experience import Experience





T = TypeVar("T", bound="ListExperiencesOutput")



@_attrs_define
class ListExperiencesOutput:
    """ 
        Attributes:
            experiences (list[Experience] | Unset):
            next_page_token (str | Unset):
            total (int | Unset):
     """

    experiences: list[Experience] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience import Experience
        experiences: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.experiences, Unset):
            experiences = []
            for experiences_item_data in self.experiences:
                experiences_item = experiences_item_data.to_dict()
                experiences.append(experiences_item)



        next_page_token = self.next_page_token

        total = self.total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if experiences is not UNSET:
            field_dict["experiences"] = experiences
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience import Experience
        d = dict(src_dict)
        experiences = []
        _experiences = d.pop("experiences", UNSET)
        for experiences_item_data in (_experiences or []):
            experiences_item = Experience.from_dict(experiences_item_data)



            experiences.append(experiences_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        total = d.pop("total", UNSET)

        list_experiences_output = cls(
            experiences=experiences,
            next_page_token=next_page_token,
            total=total,
        )


        list_experiences_output.additional_properties = d
        return list_experiences_output

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
