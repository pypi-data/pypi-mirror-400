from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.event import Event





T = TypeVar("T", bound="ListJobEventsOutput")



@_attrs_define
class ListJobEventsOutput:
    """ 
        Attributes:
            events (list[Event] | Unset):
            next_page_token (str | Unset):
     """

    events: list[Event] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.event import Event
        events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.events, Unset):
            events = []
            for events_item_data in self.events:
                events_item = events_item_data.to_dict()
                events.append(events_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if events is not UNSET:
            field_dict["events"] = events
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event import Event
        d = dict(src_dict)
        events = []
        _events = d.pop("events", UNSET)
        for events_item_data in (_events or []):
            events_item = Event.from_dict(events_item_data)



            events.append(events_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_job_events_output = cls(
            events=events,
            next_page_token=next_page_token,
        )


        list_job_events_output.additional_properties = d
        return list_job_events_output

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
