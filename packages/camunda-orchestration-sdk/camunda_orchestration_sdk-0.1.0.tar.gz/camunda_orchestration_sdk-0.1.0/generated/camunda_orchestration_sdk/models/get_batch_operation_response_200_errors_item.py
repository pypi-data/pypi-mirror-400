from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_batch_operation_response_200_errors_item_type import (
    GetBatchOperationResponse200ErrorsItemType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetBatchOperationResponse200ErrorsItem")


@_attrs_define
class GetBatchOperationResponse200ErrorsItem:
    """
    Attributes:
        partition_id (int | Unset): The partition ID where the error occurred.
        type_ (GetBatchOperationResponse200ErrorsItemType | Unset): The type of the error that occurred during the batch
            operation.
        message (str | Unset): The error message that occurred during the batch operation.
    """

    partition_id: int | Unset = UNSET
    type_: GetBatchOperationResponse200ErrorsItemType | Unset = UNSET
    message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        partition_id = self.partition_id

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if partition_id is not UNSET:
            field_dict["partitionId"] = partition_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        partition_id = d.pop("partitionId", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: GetBatchOperationResponse200ErrorsItemType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = GetBatchOperationResponse200ErrorsItemType(_type_)

        message = d.pop("message", UNSET)

        get_batch_operation_response_200_errors_item = cls(
            partition_id=partition_id,
            type_=type_,
            message=message,
        )

        get_batch_operation_response_200_errors_item.additional_properties = d
        return get_batch_operation_response_200_errors_item

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
