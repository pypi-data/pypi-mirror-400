from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_experience_tag_fields import UpdateExperienceTagFields





T = TypeVar("T", bound="UpdateExperienceTagInput")



@_attrs_define
class UpdateExperienceTagInput:
    """ 
        Attributes:
            update_mask (list[str] | Unset):
            experience_tag (UpdateExperienceTagFields | Unset):
     """

    update_mask: list[str] | Unset = UNSET
    experience_tag: UpdateExperienceTagFields | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_experience_tag_fields import UpdateExperienceTagFields
        update_mask: list[str] | Unset = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask



        experience_tag: dict[str, Any] | Unset = UNSET
        if not isinstance(self.experience_tag, Unset):
            experience_tag = self.experience_tag.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask
        if experience_tag is not UNSET:
            field_dict["experienceTag"] = experience_tag

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_experience_tag_fields import UpdateExperienceTagFields
        d = dict(src_dict)
        update_mask = cast(list[str], d.pop("updateMask", UNSET))


        _experience_tag = d.pop("experienceTag", UNSET)
        experience_tag: UpdateExperienceTagFields | Unset
        if isinstance(_experience_tag,  Unset):
            experience_tag = UNSET
        else:
            experience_tag = UpdateExperienceTagFields.from_dict(_experience_tag)




        update_experience_tag_input = cls(
            update_mask=update_mask,
            experience_tag=experience_tag,
        )


        update_experience_tag_input.additional_properties = d
        return update_experience_tag_input

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
