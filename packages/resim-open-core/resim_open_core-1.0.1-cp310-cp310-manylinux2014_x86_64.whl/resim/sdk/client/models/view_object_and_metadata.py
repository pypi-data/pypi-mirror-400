from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.view_object import ViewObject
  from ..models.view_metadata import ViewMetadata





T = TypeVar("T", bound="ViewObjectAndMetadata")



@_attrs_define
class ViewObjectAndMetadata:
    """ 
        Attributes:
            view_object (ViewObject | Unset):
            view_metadata (list[ViewMetadata] | Unset):
     """

    view_object: ViewObject | Unset = UNSET
    view_metadata: list[ViewMetadata] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.view_object import ViewObject
        from ..models.view_metadata import ViewMetadata
        view_object: dict[str, Any] | Unset = UNSET
        if not isinstance(self.view_object, Unset):
            view_object = self.view_object.to_dict()

        view_metadata: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.view_metadata, Unset):
            view_metadata = []
            for view_metadata_item_data in self.view_metadata:
                view_metadata_item = view_metadata_item_data.to_dict()
                view_metadata.append(view_metadata_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if view_object is not UNSET:
            field_dict["viewObject"] = view_object
        if view_metadata is not UNSET:
            field_dict["viewMetadata"] = view_metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.view_object import ViewObject
        from ..models.view_metadata import ViewMetadata
        d = dict(src_dict)
        _view_object = d.pop("viewObject", UNSET)
        view_object: ViewObject | Unset
        if isinstance(_view_object,  Unset):
            view_object = UNSET
        else:
            view_object = ViewObject.from_dict(_view_object)




        view_metadata = []
        _view_metadata = d.pop("viewMetadata", UNSET)
        for view_metadata_item_data in (_view_metadata or []):
            view_metadata_item = ViewMetadata.from_dict(view_metadata_item_data)



            view_metadata.append(view_metadata_item)


        view_object_and_metadata = cls(
            view_object=view_object,
            view_metadata=view_metadata,
        )


        view_object_and_metadata.additional_properties = d
        return view_object_and_metadata

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
