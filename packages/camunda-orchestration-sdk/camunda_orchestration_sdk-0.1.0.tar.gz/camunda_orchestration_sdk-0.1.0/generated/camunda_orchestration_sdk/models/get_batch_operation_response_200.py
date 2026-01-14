from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_batch_operation_response_200_actor_type import (
    GetBatchOperationResponse200ActorType,
)
from ..models.get_batch_operation_response_200_batch_operation_type import (
    GetBatchOperationResponse200BatchOperationType,
)
from ..models.get_batch_operation_response_200_state import (
    GetBatchOperationResponse200State,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_batch_operation_response_200_errors_item import (
        GetBatchOperationResponse200ErrorsItem,
    )


T = TypeVar("T", bound="GetBatchOperationResponse200")


@_attrs_define
class GetBatchOperationResponse200:
    """
    Attributes:
        batch_operation_key (str | Unset): Key or (Operate Legacy ID = UUID) of the batch operation. Example:
            2251799813684321.
        state (GetBatchOperationResponse200State | Unset): The batch operation state.
        batch_operation_type (GetBatchOperationResponse200BatchOperationType | Unset): The type of the batch operation.
        start_date (datetime.datetime | Unset): The start date of the batch operation.
        end_date (datetime.datetime | Unset): The end date of the batch operation.
        actor_type (GetBatchOperationResponse200ActorType | Unset): The type of the actor. Available for batch
            operations created since 8.9.
        actor_id (str | Unset): The ID of the actor who performed the operation. Available for batch operations created
            since 8.9.
        operations_total_count (int | Unset): The total number of items contained in this batch operation.
        operations_failed_count (int | Unset): The number of items which failed during execution of the batch operation.
            (e.g. because they are rejected by the Zeebe engine).
        operations_completed_count (int | Unset): The number of successfully completed tasks.
        errors (list[GetBatchOperationResponse200ErrorsItem] | Unset): The errors that occurred per partition during the
            batch operation.
    """

    batch_operation_key: BatchOperationKey | Unset = UNSET
    state: GetBatchOperationResponse200State | Unset = UNSET
    batch_operation_type: GetBatchOperationResponse200BatchOperationType | Unset = UNSET
    start_date: datetime.datetime | Unset = UNSET
    end_date: datetime.datetime | Unset = UNSET
    actor_type: GetBatchOperationResponse200ActorType | Unset = UNSET
    actor_id: str | Unset = UNSET
    operations_total_count: int | Unset = UNSET
    operations_failed_count: int | Unset = UNSET
    operations_completed_count: int | Unset = UNSET
    errors: list[GetBatchOperationResponse200ErrorsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        batch_operation_key = self.batch_operation_key

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        batch_operation_type: str | Unset = UNSET
        if not isinstance(self.batch_operation_type, Unset):
            batch_operation_type = self.batch_operation_type.value

        start_date: str | Unset = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: str | Unset = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        actor_type: str | Unset = UNSET
        if not isinstance(self.actor_type, Unset):
            actor_type = self.actor_type.value

        actor_id = self.actor_id

        operations_total_count = self.operations_total_count

        operations_failed_count = self.operations_failed_count

        operations_completed_count = self.operations_completed_count

        errors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch_operation_key is not UNSET:
            field_dict["batchOperationKey"] = batch_operation_key
        if state is not UNSET:
            field_dict["state"] = state
        if batch_operation_type is not UNSET:
            field_dict["batchOperationType"] = batch_operation_type
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if actor_type is not UNSET:
            field_dict["actorType"] = actor_type
        if actor_id is not UNSET:
            field_dict["actorId"] = actor_id
        if operations_total_count is not UNSET:
            field_dict["operationsTotalCount"] = operations_total_count
        if operations_failed_count is not UNSET:
            field_dict["operationsFailedCount"] = operations_failed_count
        if operations_completed_count is not UNSET:
            field_dict["operationsCompletedCount"] = operations_completed_count
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_batch_operation_response_200_errors_item import (
            GetBatchOperationResponse200ErrorsItem,
        )

        d = dict(src_dict)
        batch_operation_key = lift_batch_operation_key(_val) if (_val := d.pop("batchOperationKey", UNSET)) is not UNSET else UNSET

        _state = d.pop("state", UNSET)
        state: GetBatchOperationResponse200State | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = GetBatchOperationResponse200State(_state)

        _batch_operation_type = d.pop("batchOperationType", UNSET)
        batch_operation_type: GetBatchOperationResponse200BatchOperationType | Unset
        if isinstance(_batch_operation_type, Unset):
            batch_operation_type = UNSET
        else:
            batch_operation_type = GetBatchOperationResponse200BatchOperationType(
                _batch_operation_type
            )

        _start_date = d.pop("startDate", UNSET)
        start_date: datetime.datetime | Unset
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: datetime.datetime | Unset
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        _actor_type = d.pop("actorType", UNSET)
        actor_type: GetBatchOperationResponse200ActorType | Unset
        if isinstance(_actor_type, Unset):
            actor_type = UNSET
        else:
            actor_type = GetBatchOperationResponse200ActorType(_actor_type)

        actor_id = d.pop("actorId", UNSET)

        operations_total_count = d.pop("operationsTotalCount", UNSET)

        operations_failed_count = d.pop("operationsFailedCount", UNSET)

        operations_completed_count = d.pop("operationsCompletedCount", UNSET)

        _errors = d.pop("errors", UNSET)
        errors: list[GetBatchOperationResponse200ErrorsItem] | Unset = UNSET
        if _errors is not UNSET:
            errors = []
            for errors_item_data in _errors:
                errors_item = GetBatchOperationResponse200ErrorsItem.from_dict(
                    errors_item_data
                )

                errors.append(errors_item)

        get_batch_operation_response_200 = cls(
            batch_operation_key=batch_operation_key,
            state=state,
            batch_operation_type=batch_operation_type,
            start_date=start_date,
            end_date=end_date,
            actor_type=actor_type,
            actor_id=actor_id,
            operations_total_count=operations_total_count,
            operations_failed_count=operations_failed_count,
            operations_completed_count=operations_completed_count,
            errors=errors,
        )

        get_batch_operation_response_200.additional_properties = d
        return get_batch_operation_response_200

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
