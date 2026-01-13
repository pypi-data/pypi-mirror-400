from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.parameter_sweep import ParameterSweep





T = TypeVar("T", bound="ListParameterSweepsOutput")



@_attrs_define
class ListParameterSweepsOutput:
    """ 
        Attributes:
            sweeps (list[ParameterSweep] | Unset):
            next_page_token (str | Unset):
     """

    sweeps: list[ParameterSweep] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.parameter_sweep import ParameterSweep
        sweeps: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sweeps, Unset):
            sweeps = []
            for sweeps_item_data in self.sweeps:
                sweeps_item = sweeps_item_data.to_dict()
                sweeps.append(sweeps_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if sweeps is not UNSET:
            field_dict["sweeps"] = sweeps
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parameter_sweep import ParameterSweep
        d = dict(src_dict)
        sweeps = []
        _sweeps = d.pop("sweeps", UNSET)
        for sweeps_item_data in (_sweeps or []):
            sweeps_item = ParameterSweep.from_dict(sweeps_item_data)



            sweeps.append(sweeps_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_parameter_sweeps_output = cls(
            sweeps=sweeps,
            next_page_token=next_page_token,
        )


        list_parameter_sweeps_output.additional_properties = d
        return list_parameter_sweeps_output

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
