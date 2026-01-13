from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.triggered_via import TriggeredVia
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.batch_parameters import BatchParameters





T = TypeVar("T", bound="TestSuiteBatchInput")



@_attrs_define
class TestSuiteBatchInput:
    """ 
        Attributes:
            build_id (str):
            batch_name (str | Unset):
            parameters (BatchParameters | Unset):
            associated_account (str | Unset):
            triggered_via (TriggeredVia | Unset):
            pool_labels (list[str] | Unset):
            allowable_failure_percent (int | None | Unset):
     """

    build_id: str
    batch_name: str | Unset = UNSET
    parameters: BatchParameters | Unset = UNSET
    associated_account: str | Unset = UNSET
    triggered_via: TriggeredVia | Unset = UNSET
    pool_labels: list[str] | Unset = UNSET
    allowable_failure_percent: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_parameters import BatchParameters
        build_id = self.build_id

        batch_name = self.batch_name

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        associated_account = self.associated_account

        triggered_via: str | Unset = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value


        pool_labels: list[str] | Unset = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels



        allowable_failure_percent: int | None | Unset
        if isinstance(self.allowable_failure_percent, Unset):
            allowable_failure_percent = UNSET
        else:
            allowable_failure_percent = self.allowable_failure_percent


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "buildID": build_id,
        })
        if batch_name is not UNSET:
            field_dict["batchName"] = batch_name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels
        if allowable_failure_percent is not UNSET:
            field_dict["allowableFailurePercent"] = allowable_failure_percent

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_parameters import BatchParameters
        d = dict(src_dict)
        build_id = d.pop("buildID")

        batch_name = d.pop("batchName", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: BatchParameters | Unset
        if isinstance(_parameters,  Unset):
            parameters = UNSET
        else:
            parameters = BatchParameters.from_dict(_parameters)




        associated_account = d.pop("associatedAccount", UNSET)

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: TriggeredVia | Unset
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        pool_labels = cast(list[str], d.pop("poolLabels", UNSET))


        def _parse_allowable_failure_percent(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        allowable_failure_percent = _parse_allowable_failure_percent(d.pop("allowableFailurePercent", UNSET))


        test_suite_batch_input = cls(
            build_id=build_id,
            batch_name=batch_name,
            parameters=parameters,
            associated_account=associated_account,
            triggered_via=triggered_via,
            pool_labels=pool_labels,
            allowable_failure_percent=allowable_failure_percent,
        )


        test_suite_batch_input.additional_properties = d
        return test_suite_batch_input

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
