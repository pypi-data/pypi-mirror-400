from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_experience_fields import UpdateExperienceFields





T = TypeVar("T", bound="UpdateExperienceInput")



@_attrs_define
class UpdateExperienceInput:
    """ 
        Attributes:
            update_mask (list[str] | Unset):
            experience (UpdateExperienceFields | Unset):
     """

    update_mask: list[str] | Unset = UNSET
    experience: UpdateExperienceFields | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_experience_fields import UpdateExperienceFields
        update_mask: list[str] | Unset = UNSET
        if not isinstance(self.update_mask, Unset):
            update_mask = self.update_mask



        experience: dict[str, Any] | Unset = UNSET
        if not isinstance(self.experience, Unset):
            experience = self.experience.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if update_mask is not UNSET:
            field_dict["updateMask"] = update_mask
        if experience is not UNSET:
            field_dict["experience"] = experience

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_experience_fields import UpdateExperienceFields
        d = dict(src_dict)
        update_mask = cast(list[str], d.pop("updateMask", UNSET))


        _experience = d.pop("experience", UNSET)
        experience: UpdateExperienceFields | Unset
        if isinstance(_experience,  Unset):
            experience = UNSET
        else:
            experience = UpdateExperienceFields.from_dict(_experience)




        update_experience_input = cls(
            update_mask=update_mask,
            experience=experience,
        )


        update_experience_input.additional_properties = d
        return update_experience_input

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
