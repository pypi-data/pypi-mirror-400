from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.experience_tag import ExperienceTag





T = TypeVar("T", bound="ListExperienceTagsOutput")



@_attrs_define
class ListExperienceTagsOutput:
    """ 
        Attributes:
            experience_tags (list[ExperienceTag] | Unset):
            next_page_token (str | Unset):
     """

    experience_tags: list[ExperienceTag] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_tag import ExperienceTag
        experience_tags: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.experience_tags, Unset):
            experience_tags = []
            for experience_tags_item_data in self.experience_tags:
                experience_tags_item = experience_tags_item_data.to_dict()
                experience_tags.append(experience_tags_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if experience_tags is not UNSET:
            field_dict["experienceTags"] = experience_tags
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_tag import ExperienceTag
        d = dict(src_dict)
        experience_tags = []
        _experience_tags = d.pop("experienceTags", UNSET)
        for experience_tags_item_data in (_experience_tags or []):
            experience_tags_item = ExperienceTag.from_dict(experience_tags_item_data)



            experience_tags.append(experience_tags_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_experience_tags_output = cls(
            experience_tags=experience_tags,
            next_page_token=next_page_token,
        )


        list_experience_tags_output.additional_properties = d
        return list_experience_tags_output

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
