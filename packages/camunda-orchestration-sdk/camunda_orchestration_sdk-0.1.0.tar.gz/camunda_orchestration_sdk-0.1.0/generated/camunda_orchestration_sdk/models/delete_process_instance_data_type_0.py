from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteProcessInstanceDataType0")


@_attrs_define
class DeleteProcessInstanceDataType0:
    """
    Attributes:
        operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
            from this operation.
            Must be > 0 if provided.
    """

    operation_reference: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        operation_reference = self.operation_reference

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation_reference = d.pop("operationReference", UNSET)

        delete_process_instance_data_type_0 = cls(
            operation_reference=operation_reference,
        )

        return delete_process_instance_data_type_0
