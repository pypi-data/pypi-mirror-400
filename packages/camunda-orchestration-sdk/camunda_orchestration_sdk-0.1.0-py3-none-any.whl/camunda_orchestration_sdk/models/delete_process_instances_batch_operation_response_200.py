from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.delete_process_instances_batch_operation_response_200_batch_operation_type import (
    DeleteProcessInstancesBatchOperationResponse200BatchOperationType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteProcessInstancesBatchOperationResponse200")


@_attrs_define
class DeleteProcessInstancesBatchOperationResponse200:
    """The created batch operation.

    Attributes:
        batch_operation_key (str | Unset): Key of the batch operation. Example: 2251799813684321.
        batch_operation_type (DeleteProcessInstancesBatchOperationResponse200BatchOperationType | Unset): The type of
            the batch operation.
    """

    batch_operation_key: BatchOperationKey | Unset = UNSET
    batch_operation_type: (
        DeleteProcessInstancesBatchOperationResponse200BatchOperationType | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        batch_operation_key = self.batch_operation_key

        batch_operation_type: str | Unset = UNSET
        if not isinstance(self.batch_operation_type, Unset):
            batch_operation_type = self.batch_operation_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch_operation_key is not UNSET:
            field_dict["batchOperationKey"] = batch_operation_key
        if batch_operation_type is not UNSET:
            field_dict["batchOperationType"] = batch_operation_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        batch_operation_key = lift_batch_operation_key(_val) if (_val := d.pop("batchOperationKey", UNSET)) is not UNSET else UNSET

        _batch_operation_type = d.pop("batchOperationType", UNSET)
        batch_operation_type: (
            DeleteProcessInstancesBatchOperationResponse200BatchOperationType | Unset
        )
        if isinstance(_batch_operation_type, Unset):
            batch_operation_type = UNSET
        else:
            batch_operation_type = (
                DeleteProcessInstancesBatchOperationResponse200BatchOperationType(
                    _batch_operation_type
                )
            )

        delete_process_instances_batch_operation_response_200 = cls(
            batch_operation_key=batch_operation_key,
            batch_operation_type=batch_operation_type,
        )

        delete_process_instances_batch_operation_response_200.additional_properties = d
        return delete_process_instances_batch_operation_response_200

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
