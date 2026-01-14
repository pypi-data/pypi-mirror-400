from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_batch_operation_items_response_200_items_item_operation_type import (
    SearchBatchOperationItemsResponse200ItemsItemOperationType,
)
from ..models.search_batch_operation_items_response_200_items_item_state import (
    SearchBatchOperationItemsResponse200ItemsItemState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchBatchOperationItemsResponse200ItemsItem")


@_attrs_define
class SearchBatchOperationItemsResponse200ItemsItem:
    """
    Attributes:
        operation_type (SearchBatchOperationItemsResponse200ItemsItemOperationType | Unset): The type of the batch
            operation.
        batch_operation_key (str | Unset): The key (or operate legacy ID) of the batch operation. Example:
            2251799813684321.
        item_key (str | Unset): Key of the item, e.g. a process instance key.
        process_instance_key (str | Unset): the process instance key of the processed item. Example: 2251799813690746.
        state (SearchBatchOperationItemsResponse200ItemsItemState | Unset): State of the item.
        processed_date (datetime.datetime | Unset): the date this item was processed.
        error_message (str | Unset): the error message from the engine in case of a failed operation.
    """

    operation_type: (
        SearchBatchOperationItemsResponse200ItemsItemOperationType | Unset
    ) = UNSET
    batch_operation_key: BatchOperationKey | Unset = UNSET
    item_key: str | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    state: SearchBatchOperationItemsResponse200ItemsItemState | Unset = UNSET
    processed_date: datetime.datetime | Unset = UNSET
    error_message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operation_type: str | Unset = UNSET
        if not isinstance(self.operation_type, Unset):
            operation_type = self.operation_type.value

        batch_operation_key = self.batch_operation_key

        item_key = self.item_key

        process_instance_key = self.process_instance_key

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        processed_date: str | Unset = UNSET
        if not isinstance(self.processed_date, Unset):
            processed_date = self.processed_date.isoformat()

        error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if batch_operation_key is not UNSET:
            field_dict["batchOperationKey"] = batch_operation_key
        if item_key is not UNSET:
            field_dict["itemKey"] = item_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if state is not UNSET:
            field_dict["state"] = state
        if processed_date is not UNSET:
            field_dict["processedDate"] = processed_date
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _operation_type = d.pop("operationType", UNSET)
        operation_type: (
            SearchBatchOperationItemsResponse200ItemsItemOperationType | Unset
        )
        if isinstance(_operation_type, Unset):
            operation_type = UNSET
        else:
            operation_type = SearchBatchOperationItemsResponse200ItemsItemOperationType(
                _operation_type
            )

        batch_operation_key = lift_batch_operation_key(_val) if (_val := d.pop("batchOperationKey", UNSET)) is not UNSET else UNSET

        item_key = d.pop("itemKey", UNSET)

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        _state = d.pop("state", UNSET)
        state: SearchBatchOperationItemsResponse200ItemsItemState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = SearchBatchOperationItemsResponse200ItemsItemState(_state)

        _processed_date = d.pop("processedDate", UNSET)
        processed_date: datetime.datetime | Unset
        if isinstance(_processed_date, Unset):
            processed_date = UNSET
        else:
            processed_date = isoparse(_processed_date)

        error_message = d.pop("errorMessage", UNSET)

        search_batch_operation_items_response_200_items_item = cls(
            operation_type=operation_type,
            batch_operation_key=batch_operation_key,
            item_key=item_key,
            process_instance_key=process_instance_key,
            state=state,
            processed_date=processed_date,
            error_message=error_message,
        )

        search_batch_operation_items_response_200_items_item.additional_properties = d
        return search_batch_operation_items_response_200_items_item

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
