from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.execution_error_metadata import ExecutionErrorMetadata





T = TypeVar("T", bound="ExecutionError")



@_attrs_define
class ExecutionError:
    """ 
        Attributes:
            error_code (str): Standardized error code (e.g., UNKNOWN_ERROR, NONZERO_EXIT_CODE)
            error_text (str | Unset): Error text
            run_counter (int | Unset): Run counter of the error
            parent_id (str | Unset): ID of the parent object (e.g., job ID, batch ID)
            parent_type (str | Unset): Type of the parent object (e.g., JOB, BATCH)
            metadata (ExecutionErrorMetadata | Unset): Error metadata
     """

    error_code: str
    error_text: str | Unset = UNSET
    run_counter: int | Unset = UNSET
    parent_id: str | Unset = UNSET
    parent_type: str | Unset = UNSET
    metadata: ExecutionErrorMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.execution_error_metadata import ExecutionErrorMetadata
        error_code = self.error_code

        error_text = self.error_text

        run_counter = self.run_counter

        parent_id = self.parent_id

        parent_type = self.parent_type

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "errorCode": error_code,
        })
        if error_text is not UNSET:
            field_dict["errorText"] = error_text
        if run_counter is not UNSET:
            field_dict["runCounter"] = run_counter
        if parent_id is not UNSET:
            field_dict["parentID"] = parent_id
        if parent_type is not UNSET:
            field_dict["parentType"] = parent_type
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execution_error_metadata import ExecutionErrorMetadata
        d = dict(src_dict)
        error_code = d.pop("errorCode")

        error_text = d.pop("errorText", UNSET)

        run_counter = d.pop("runCounter", UNSET)

        parent_id = d.pop("parentID", UNSET)

        parent_type = d.pop("parentType", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: ExecutionErrorMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = ExecutionErrorMetadata.from_dict(_metadata)




        execution_error = cls(
            error_code=error_code,
            error_text=error_text,
            run_counter=run_counter,
            parent_id=parent_id,
            parent_type=parent_type,
            metadata=metadata,
        )


        execution_error.additional_properties = d
        return execution_error

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
