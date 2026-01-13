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





T = TypeVar("T", bound="ListViewObjectsOutput")



@_attrs_define
class ListViewObjectsOutput:
    """ 
        Attributes:
            view_sessions (list[ViewObject] | Unset):
            next_page_token (str | Unset):
     """

    view_sessions: list[ViewObject] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.view_object import ViewObject
        view_sessions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.view_sessions, Unset):
            view_sessions = []
            for view_sessions_item_data in self.view_sessions:
                view_sessions_item = view_sessions_item_data.to_dict()
                view_sessions.append(view_sessions_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if view_sessions is not UNSET:
            field_dict["viewSessions"] = view_sessions
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.view_object import ViewObject
        d = dict(src_dict)
        view_sessions = []
        _view_sessions = d.pop("viewSessions", UNSET)
        for view_sessions_item_data in (_view_sessions or []):
            view_sessions_item = ViewObject.from_dict(view_sessions_item_data)



            view_sessions.append(view_sessions_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_view_objects_output = cls(
            view_sessions=view_sessions,
            next_page_token=next_page_token,
        )


        list_view_objects_output.additional_properties = d
        return list_view_objects_output

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
