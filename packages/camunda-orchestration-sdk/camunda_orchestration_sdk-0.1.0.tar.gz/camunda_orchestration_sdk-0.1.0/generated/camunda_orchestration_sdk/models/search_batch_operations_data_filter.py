from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.operationtype_exactmatch_1 import OperationtypeExactmatch1
from ..models.search_batch_operations_data_filter_actor_type import (
    SearchBatchOperationsDataFilterActorType,
)
from ..models.state_exactmatch_1 import StateExactmatch1
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter
    from ..models.batchoperationkey_advancedfilter import (
        BatchoperationkeyAdvancedfilter,
    )
    from ..models.operationtype_advancedfilter_1 import OperationtypeAdvancedfilter1
    from ..models.state_advancedfilter_1 import StateAdvancedfilter1


T = TypeVar("T", bound="SearchBatchOperationsDataFilter")


@_attrs_define
class SearchBatchOperationsDataFilter:
    """The batch operation search filters.

    Attributes:
        batch_operation_key (BatchoperationkeyAdvancedfilter | str | Unset):
        operation_type (OperationtypeAdvancedfilter1 | OperationtypeExactmatch1 | Unset):
        state (StateAdvancedfilter1 | StateExactmatch1 | Unset):
        actor_type (SearchBatchOperationsDataFilterActorType | Unset): The type of the actor who performed the
            operation.
        actor_id (ActoridAdvancedfilter | str | Unset):
    """

    batch_operation_key: BatchoperationkeyAdvancedfilter | str | Unset = UNSET
    operation_type: OperationtypeAdvancedfilter1 | OperationtypeExactmatch1 | Unset = (
        UNSET
    )
    state: StateAdvancedfilter1 | StateExactmatch1 | Unset = UNSET
    actor_type: SearchBatchOperationsDataFilterActorType | Unset = UNSET
    actor_id: ActoridAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.batchoperationkey_advancedfilter import (
            BatchoperationkeyAdvancedfilter,
        )

        batch_operation_key: dict[str, Any] | str | Unset
        if isinstance(self.batch_operation_key, Unset):
            batch_operation_key = UNSET
        elif isinstance(self.batch_operation_key, BatchoperationkeyAdvancedfilter):
            batch_operation_key = self.batch_operation_key.to_dict()
        else:
            batch_operation_key = self.batch_operation_key

        operation_type: dict[str, Any] | str | Unset
        if isinstance(self.operation_type, Unset):
            operation_type = UNSET
        elif isinstance(self.operation_type, OperationtypeExactmatch1):
            operation_type = self.operation_type.value
        else:
            operation_type = self.operation_type.to_dict()

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch1):
            state = self.state.value
        else:
            state = self.state.to_dict()

        actor_type: str | Unset = UNSET
        if not isinstance(self.actor_type, Unset):
            actor_type = self.actor_type.value

        actor_id: dict[str, Any] | str | Unset
        if isinstance(self.actor_id, Unset):
            actor_id = UNSET
        elif isinstance(self.actor_id, ActoridAdvancedfilter):
            actor_id = self.actor_id.to_dict()
        else:
            actor_id = self.actor_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch_operation_key is not UNSET:
            field_dict["batchOperationKey"] = batch_operation_key
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if state is not UNSET:
            field_dict["state"] = state
        if actor_type is not UNSET:
            field_dict["actorType"] = actor_type
        if actor_id is not UNSET:
            field_dict["actorId"] = actor_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter
        from ..models.batchoperationkey_advancedfilter import (
            BatchoperationkeyAdvancedfilter,
        )
        from ..models.operationtype_advancedfilter_1 import OperationtypeAdvancedfilter1
        from ..models.state_advancedfilter_1 import StateAdvancedfilter1

        d = dict(src_dict)

        def _parse_batch_operation_key(
            data: object,
        ) -> BatchoperationkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                batch_operation_key_type_1 = BatchoperationkeyAdvancedfilter.from_dict(
                    data
                )

                return batch_operation_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BatchoperationkeyAdvancedfilter | str | Unset, data)

        batch_operation_key = _parse_batch_operation_key(
            d.pop("batchOperationKey", UNSET)
        )

        def _parse_operation_type(
            data: object,
        ) -> OperationtypeAdvancedfilter1 | OperationtypeExactmatch1 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operation_type_type_0 = OperationtypeExactmatch1(data)

                return operation_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            operation_type_type_1 = OperationtypeAdvancedfilter1.from_dict(data)

            return operation_type_type_1

        operation_type = _parse_operation_type(d.pop("operationType", UNSET))

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter1 | StateExactmatch1 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch1(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter1.from_dict(data)

            return state_type_1

        state = _parse_state(d.pop("state", UNSET))

        _actor_type = d.pop("actorType", UNSET)
        actor_type: SearchBatchOperationsDataFilterActorType | Unset
        if isinstance(_actor_type, Unset):
            actor_type = UNSET
        else:
            actor_type = SearchBatchOperationsDataFilterActorType(_actor_type)

        def _parse_actor_id(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_id_type_1 = ActoridAdvancedfilter.from_dict(data)

                return actor_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        actor_id = _parse_actor_id(d.pop("actorId", UNSET))

        search_batch_operations_data_filter = cls(
            batch_operation_key=batch_operation_key,
            operation_type=operation_type,
            state=state,
            actor_type=actor_type,
            actor_id=actor_id,
        )

        search_batch_operations_data_filter.additional_properties = d
        return search_batch_operations_data_filter

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
